// Recorte de persona con Vision (macOS), fotograma a fotograma.
// Uso: personas <video> <carpeta_mascaras> <salida.json> [fps]
// - Guarda una PNG por fotograma (m_00000.png …) de 270x480: transparente donde está la persona y opaca en el
//   fondo. En Remotion se usa como máscara: lo que va "detrás" solo se ve fuera de la persona.
// - En el JSON guarda, por fotograma, la fila más alta de la persona en la franja central (cabeza)
//   y el ancho de la cabeza: [{ "t": s, "cabeza": y, "x0": x, "x1": x }] (fracciones de la pantalla).
import AVFoundation
import CoreImage
import Foundation
import ImageIO
import UniformTypeIdentifiers
import Vision

let args = CommandLine.arguments
guard args.count >= 4 else {
    print("Uso: personas <video> <carpeta> <salida.json> [fps]")
    exit(1)
}
let asset = AVURLAsset(url: URL(fileURLWithPath: args[1]))
let carpeta = URL(fileURLWithPath: args[2], isDirectory: true)
let salida = URL(fileURLWithPath: args[3])
let fps = args.count > 4 ? Double(args[4]) ?? 30 : 30
try FileManager.default.createDirectory(at: carpeta, withIntermediateDirectories: true)

let generador = AVAssetImageGenerator(asset: asset)
generador.appliesPreferredTrackTransform = true
generador.requestedTimeToleranceBefore = .zero
generador.requestedTimeToleranceAfter = .zero
generador.maximumSize = CGSize(width: 540, height: 960)

let ancho = 270, alto = 480
let total = Int(CMTimeGetSeconds(asset.duration) * fps)
var datos: [[String: Double]] = []

for n in 0..<total {
    let t = Double(n) / fps
    guard let imagen = try? generador.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil) else { continue }
    let pedido = VNGeneratePersonSegmentationRequest()
    pedido.qualityLevel = .accurate
    pedido.outputPixelFormat = kCVPixelFormatType_OneComponent8
    try? VNImageRequestHandler(cgImage: imagen, options: [:]).perform([pedido])
    guard let mascara = pedido.results?.first?.pixelBuffer else { continue }

    // Escalar la máscara a 270x480 en escala de grises
    // Silueta limpia: cierra los huecos entre mechones (dilatar y luego erosionar) y suaviza el borde,
    // así el texto no queda "intercalado" con el pelo.
    var ci = CIImage(cvPixelBuffer: mascara)
    let radio = max(2.0, ci.extent.width / 120)
    ci = ci.applyingFilter("CIMorphologyMaximum", parameters: ["inputRadius": radio])
        .applyingFilter("CIMorphologyMinimum", parameters: ["inputRadius": radio * 0.7])
        .cropped(to: ci.extent)
        .applyingFilter("CIGaussianBlur", parameters: ["inputRadius": radio * 0.5])
        .cropped(to: CIImage(cvPixelBuffer: mascara).extent)
    let escala = CGAffineTransform(scaleX: CGFloat(ancho) / ci.extent.width, y: CGFloat(alto) / ci.extent.height)
    var gris = [UInt8](repeating: 0, count: ancho * alto)
    let contexto = CIContext()
    contexto.render(ci.transformed(by: escala), toBitmap: &gris, rowBytes: ancho, bounds: CGRect(x: 0, y: 0, width: ancho, height: alto),
                    format: .L8, colorSpace: nil)

    // RGBA blanco con alfa = 255 - persona
    var rgba = [UInt8](repeating: 255, count: ancho * alto * 4)
    for i in 0..<(ancho * alto) { rgba[i * 4 + 3] = 255 - gris[i] }
    let proveedor = CGDataProvider(data: Data(rgba) as CFData)!
    let cg = CGImage(width: ancho, height: alto, bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: ancho * 4,
                     space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.last.rawValue),
                     provider: proveedor, decode: nil, shouldInterpolate: true, intent: .defaultIntent)!
    let archivo = carpeta.appendingPathComponent(String(format: "m_%05d.png", n))
    if let destino = CGImageDestinationCreateWithURL(archivo as CFURL, UTType.png.identifier as CFString, 1, nil) {
        CGImageDestinationAddImage(destino, cg, nil)
        CGImageDestinationFinalize(destino)
    }

    // Cabeza: primera fila (desde arriba) con persona en la franja central 30–70 %
    var cabeza = -1
    for y in 0..<alto {
        var hay = false
        for x in (ancho * 3 / 10)..<(ancho * 7 / 10) where gris[y * ancho + x] > 128 { hay = true; break }
        if hay { cabeza = y; break }
    }
    var registro: [String: Double] = ["t": t]
    if cabeza >= 0 {
        // Ancho de la cabeza un poco más abajo de su punto más alto
        let fila = min(alto - 1, cabeza + alto / 20)
        var x0 = ancho, x1 = 0
        for x in 0..<ancho where gris[fila * ancho + x] > 128 { x0 = min(x0, x); x1 = max(x1, x) }
        registro["cabeza"] = Double(cabeza) / Double(alto)
        registro["x0"] = Double(x0) / Double(ancho)
        registro["x1"] = Double(x1) / Double(ancho)
    }
    datos.append(registro)
}
try JSONSerialization.data(withJSONObject: datos, options: []).write(to: salida)
print("\(datos.count) fotogramas procesados")
