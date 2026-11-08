// Fotogramas sueltos para revisar el look sin renderizar el vídeo entero (un solo «bundle»), como
// scripts/bridge-stills.mjs de claude-animated-shorts (Mr omi, MIT).
// Uso: node fotogramas.mjs <props.json> <prefijo_salida> <f1,f2,...> [escala] [navegador]
import path from "node:path";
import fs from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const [props, prefijo, lista, escala = "0.5", navegador] = process.argv.slice(2);
const inputProps = JSON.parse(fs.readFileSync(props, "utf8"));
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const chromiumOptions = { gl: "swangle" };
const browserExecutable = navegador || null;
const composition = await selectComposition({ serveUrl, id: "Presentador", inputProps, chromiumOptions, browserExecutable });
const onBrowserLog = (l) => { if (l.type === "error" || l.type === "warning") console.log(`[${l.type}]`, l.text.slice(0, 400)); };
for (const f of lista.split(",").map(Number)) {
  const t0 = Date.now();
  await renderStill({ composition, serveUrl, frame: f, output: `${prefijo}${String(f).padStart(4, "0")}.jpg`, imageFormat: "jpeg",
    jpegQuality: 88, scale: Number(escala), inputProps, chromiumOptions, browserExecutable, timeoutInMilliseconds: 180000, onBrowserLog });
  console.log("fotograma", f, ((Date.now() - t0) / 1000).toFixed(1) + " s");
}
