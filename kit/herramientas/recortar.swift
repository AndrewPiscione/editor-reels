// Recorta el fondo de una foto (persona, auto, objeto) con Vision y guarda un PNG transparente.
// Uso: recortar <entrada.jpg> <salida.png>
// Compilar: SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk swiftc -O recortar.swift -o recortar
import AppKit
import CoreImage
import Vision

let args = CommandLine.arguments
guard args.count == 3 else {
    print("Uso: recortar <entrada> <salida.png>")
    exit(1)
}
guard let imagen = NSImage(contentsOfFile: args[1]),
      let cg = imagen.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("No pude abrir \(args[1])")
    exit(1)
}

let pedido = VNGenerateForegroundInstanceMaskRequest()
let manejador = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try manejador.perform([pedido])
    guard let resultado = pedido.results?.first else {
        print("No encontré nada que recortar")
        exit(1)
    }
    // todas las instancias (p. ej. persona + objeto que sostiene), recortado al contenido
    let buffer = try resultado.generateMaskedImage(ofInstances: resultado.allInstances, from: manejador, croppedToInstancesExtent: true)
    let ci = CIImage(cvPixelBuffer: buffer)
    let contexto = CIContext()
    guard let salida = contexto.createCGImage(ci, from: ci.extent) else { exit(1) }
    let rep = NSBitmapImageRep(cgImage: salida)
    try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[2]))
    print("Listo: \(args[2]) (\(salida.width)×\(salida.height))")
} catch {
    print("Error: \(error)")
    exit(1)
}
