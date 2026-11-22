// Detecta la cara (y la boca) en un video con el framework Vision de macOS, cada N segundos.
// Uso: caras <video> <salida.json> [paso_en_segundos]
// Salida: [{ "t": s, "arriba": y, "abajo": y, "boca": y, "x0": x, "x1": x }], alturas en fracción (0 = arriba).
import AVFoundation
import Foundation
import Vision

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("Uso: caras <video> <salida.json> [paso]")
    exit(1)
}
let url = URL(fileURLWithPath: args[1])
let salida = URL(fileURLWithPath: args[2])
let paso = args.count > 3 ? Double(args[3]) ?? 0.2 : 0.2

let asset = AVURLAsset(url: url)
let duracion = CMTimeGetSeconds(asset.duration)
let generador = AVAssetImageGenerator(asset: asset)
generador.appliesPreferredTrackTransform = true
generador.requestedTimeToleranceBefore = CMTime(value: 1, timescale: 60)
generador.requestedTimeToleranceAfter = CMTime(value: 1, timescale: 60)
generador.maximumSize = CGSize(width: 540, height: 960)

var resultados: [[String: Double]] = []
var t = 0.0
while t < duracion {
    let tiempo = CMTime(seconds: t, preferredTimescale: 600)
    if let imagen = try? generador.copyCGImage(at: tiempo, actualTime: nil) {
        let pedido = VNDetectFaceLandmarksRequest()
        let manejador = VNImageRequestHandler(cgImage: imagen, options: [:])
        try? manejador.perform([pedido])
        // La cara más grande del cuadro
        if let cara = (pedido.results ?? []).max(by: { $0.boundingBox.width < $1.boundingBox.width }) {
            let caja = cara.boundingBox  // origen abajo-izquierda, normalizado
            var registro: [String: Double] = [
                "t": t,
                "arriba": Double(1 - caja.maxY),
                "abajo": Double(1 - caja.minY),
                "x0": Double(caja.minX),
                "x1": Double(caja.maxX),
            ]
            if let labios = cara.landmarks?.outerLips {
                let puntos = labios.normalizedPoints.map { caja.minY + $0.y * caja.height }
                if let minimo = puntos.min() { registro["boca"] = Double(1 - minimo) }
            }
            resultados.append(registro)
        }
    }
    t += paso
}
let datos = try JSONSerialization.data(withJSONObject: resultados, options: [.prettyPrinted])
try datos.write(to: salida)
print("\(resultados.count) cuadros con cara de \(Int(duracion / paso)) analizados")
