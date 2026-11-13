import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import * as pdfjs from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import type { PDFDocumentProxy, RenderTask } from "pdfjs-dist";
import "./style.css";

pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;
const MAX_SIZE = 100 * 1024 * 1024;
function App() {
  const [doc, setDoc] = useState<PDFDocumentProxy | null>(null);
  const [name, setName] = useState("");
  const [page, setPage] = useState(1);
  const [scale, setScale] = useState(1.2);
  const [renderedPage, setRenderedPage] = useState(0);
  const [message, setMessage] = useState("");
  const canvas = useRef<HTMLCanvasElement>(null);
  const generation = useRef(0);
  useEffect(() => {
    if (!doc || !canvas.current) return;
    let cancelled = false; let task: RenderTask | undefined;
    setRenderedPage(0);
    (async () => {
      try {
        const pdfPage = await doc.getPage(page);
        if (cancelled || !canvas.current) return;
        const viewport = pdfPage.getViewport({ scale });
        const surface = canvas.current; const context = surface.getContext("2d");
        if (!context) throw new Error("Không thể khởi tạo vùng hiển thị.");
        surface.width = Math.ceil(viewport.width); surface.height = Math.ceil(viewport.height);
        task = pdfPage.render({ canvas: surface, canvasContext: context, viewport });
        await task.promise;
        if (!cancelled) setRenderedPage(page);
      } catch (error) { if (!cancelled) setMessage(`Không thể hiển thị trang: ${String(error)}`); }
    })();
    return () => { cancelled = true; task?.cancel(); };
  }, [doc, page, scale]);
  useEffect(() => () => { void doc?.destroy(); }, [doc]);
  async function openFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]; event.target.value = ""; if (!file) return;
    const id = ++generation.current;
    if (file.size === 0 || file.size > MAX_SIZE) { setMessage("Tệp rỗng hoặc vượt giới hạn 100 MB."); return; }
    try {
      setMessage("Đang mở tài liệu…");
      const bytes = new Uint8Array(await file.arrayBuffer());
      if (new TextDecoder("ascii").decode(bytes.slice(0, 5)) !== "%PDF-") throw new Error("Tệp không có định dạng PDF hợp lệ.");
      const loaded = await pdfjs.getDocument({ data: bytes, isEvalSupported: false, enableXfa: false, disableAutoFetch: true }).promise;
      if (id !== generation.current) { await loaded.destroy(); return; }
      setRenderedPage(0); setDoc(loaded); setName(file.name); setPage(1); setMessage("");
    } catch (error) { if (id === generation.current) setMessage(`Không thể mở PDF. Kiểm tra tệp hoặc mật khẩu. ${String(error)}`); }
  }
  return <main className="layout">
    <aside className="library"><div className="brand"><span className="mark">L</span><div><strong>Không gian tài liệu</strong><small>Local PDF Intelligence</small></div></div><div className="section"><span className="eyebrow">NGUỒN CỤC BỘ</span><label className="open">Chọn tệp PDF<input type="file" accept=".pdf,application/pdf" onChange={openFile}/></label><p>Tệp được mở từ máy này để xem trong phiên hiện tại.</p>{doc && <div className="file" title={name}><span>PDF</span><strong>{name}</strong><small>{doc.numPages} trang</small></div>}</div></aside>
    <section className="reader"><header><div><span className="eyebrow">TRÌNH ĐỌC</span><h1>{name || "Chưa chọn tài liệu"}</h1></div><div className="controls"><button disabled={!doc || page <= 1} onClick={() => setPage(page - 1)} aria-label="Trang trước">←</button><span>{doc ? `${page} / ${doc.numPages}` : "— / —"}</span><button disabled={!doc || page >= doc.numPages} onClick={() => setPage(page + 1)} aria-label="Trang tiếp">→</button><i/><button disabled={!doc || scale <= 0.6} onClick={() => setScale(Math.max(0.6, scale - 0.2))} aria-label="Thu nhỏ">−</button><span>{Math.round(scale * 100)}%</span><button disabled={!doc || scale >= 2} onClick={() => setScale(Math.min(2, scale + 0.2))} aria-label="Phóng to">+</button></div></header>{message && <div className="notice" role="status">{message}</div>}<div className="viewport">{doc ? <canvas ref={canvas} data-rendered-page={renderedPage} aria-label={`Trang ${page} của ${name}`} style={{visibility: renderedPage === page ? "visible" : "hidden"}}/> : <div className="empty"><div className="paper">PDF</div><h2>Mở tài liệu để bắt đầu</h2><p>Chọn một tệp PDF từ máy để xem từng trang.</p></div>}</div></section>
    <aside className="research"><span className="eyebrow">NGHIÊN CỨU</span><h2>Ghi chú từ nguồn</h2><div className="pending"><span className="dot"/> Chưa khả dụng</div><p>Hỏi đáp, ghi chú và trích dẫn đang được xây dựng. Hiện có thể mở và xem PDF.</p><div className="privacy"><strong>Dữ liệu trong máy</strong><p>Trình đọc không tự tải tài liệu lên dịch vụ bên ngoài.</p></div></aside>
  </main>;
}
createRoot(document.getElementById("root")!).render(<App/>);
