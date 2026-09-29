import { useEffect, useRef, useState } from "react";
import jsQR from "jsqr";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Circle,
  Clock3,
  Database,
  Gauge,
  Globe2,
  History as HistoryIcon,
  Info,
  LoaderCircle,
  Network,
  QrCode,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Cpu,
  BarChart3,
  Layers3,
  ExternalLink,
} from "lucide-react";

const API_URL = "http://localhost:8000/api/analyze";
const VERSION = "1.0.0";
const HISTORY_KEY = "phishguard_history";

function App() {
  const [page, setPage] = useState("dashboard");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysisStage, setAnalysisStage] = useState(0);
  const [history, setHistory] = useState([]);

  const stages = [
    "Parsing URL structure",
    "Inspecting domain components",
    "Extracting security features",
    "Running ML classifier",
    "Generating threat signals",
  ];

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      setHistory(Array.isArray(saved) ? saved : []);
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    if (!loading) {
      setAnalysisStage(0);
      return;
    }

    const interval = setInterval(() => {
      setAnalysisStage((current) =>
        current < stages.length - 1 ? current + 1 : current
      );
    }, 500);

    return () => clearInterval(interval);
  }, [loading]);

  async function analyzeUrl(targetUrl = url) {
    const trimmedUrl = targetUrl.trim();

    if (!trimmedUrl) {
      setError("Enter a URL to analyze.");
      return;
    }

    setUrl(trimmedUrl);
    setPage("dashboard");
    setLoading(true);
    setError("");
    setResult(null);
    setAnalysisStage(0);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: trimmedUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to analyze URL.");
      }

      setResult(data);
      saveToHistory(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function saveToHistory(data) {
    const entry = {
      id: Date.now(),
      url: data.url,
      prediction: data.prediction,
      risk_score: data.risk_score,
      risk_level: data.risk_level,
      phishing_probability: data.phishing_probability,
      signals_count: data.signals_count,
      timestamp: new Date().toISOString(),
    };

    const existing = JSON.parse(
      localStorage.getItem(HISTORY_KEY) || "[]"
    );

    const updated = [
      entry,
      ...existing.filter((item) => item.url !== data.url),
    ].slice(0, 50);

    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    setHistory(updated);
  }

  function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    setHistory([]);
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !loading) {
      analyzeUrl();
    }
  }

  function openHistoryItem(item) {
    setUrl(item.url);
    setPage("dashboard");
    setResult(null);
    setError("");
  }

  return (
    <div className="min-h-screen bg-[#F2EDE3] text-[#111111] antialiased text-base">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-40 -top-40 h-[500px] w-[500px] rounded-full bg-[#2B2A29]/[0.025] blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-[#2B2A29]/[0.02] blur-3xl" />
      </div>

      <div className="relative flex min-h-screen">
        {/* SIDEBAR */}
        <aside className="fixed left-0 top-0 flex h-screen w-64 flex-col border-r border-[#D8D0C3] bg-[#E8E0D3]">
          <div className="border-b border-[#D8D0C3] px-7 py-7">
            <button
              onClick={() => setPage("dashboard")}
              className="flex items-center gap-3 text-left w-full"
            >
              <div>
                <div className="text-lg font-bold tracking-wider text-[#111111]">
                  PHISHGUARD
                </div>
                <div className="text-sm font-normal text-[#554F49]">
                  URL intelligence
                </div>
              </div>
            </button>
          </div>

          <nav className="flex-1 px-4 py-7 space-y-1">
            <NavSection label="Workspace" />

            <NavItem
              icon={<Gauge size={20} />}
              label="Dashboard"
              active={page === "dashboard"}
              onClick={() => setPage("dashboard")}
            />

            <NavItem
              icon={<Search size={20} />}
              label="URL Scanner"
              active={page === "scanner"}
              onClick={() => setPage("scanner")}
            />

            <NavItem
              icon={<QrCode size={20} />}
              label="QR Scanner"
              active={page === "qr"}
              onClick={() => setPage("qr")}
            />

            <NavItem
              icon={<HistoryIcon size={20} />}
              label="History"
              active={page === "history"}
              onClick={() => setPage("history")}
            />

            <div className="pt-4">
              <NavSection label="System" />
            </div>

            <NavItem
              icon={<Cpu size={20} />}
              label="Model"
              active={page === "model"}
              onClick={() => setPage("model")}
            />

            <NavItem
              icon={<Info size={20} />}
              label="About"
              active={page === "about"}
              onClick={() => setPage("about")}
            />
          </nav>

          <div className="border-t border-[#D8D0C3] p-5">
            <div className="flex items-center gap-3 rounded-xl bg-[#F2EDE3] px-4 py-3 shadow-sm">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-40" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500" />
              </span>

              <div>
                <div className="text-base font-normal text-[#111111]">
                  Engine online
                </div>
                <div className="text-sm font-normal text-[#554F49]">
                  ML analysis ready
                </div>
              </div>
            </div>

            <div className="mt-4 px-1 text-sm font-normal text-[#665E55]">
              PHISHGUARD v{VERSION}
            </div>
          </div>
        </aside>

        {/* MAIN */}
        <main className="ml-64 min-h-screen flex-1">
          <header className="flex h-20 items-center justify-between border-b border-[#D8D0C3] bg-[#EDE6DA] px-10">
            <div>
              <div className="text-xl font-normal tracking-tight text-[#111111]">
                {pageTitle(page)}
              </div>
            </div>

            <div className="flex items-center gap-3 text-base font-normal text-[#111111] bg-[#E2D9CC] px-4 py-2 rounded-full border border-[#D0C5B5] shadow-sm">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-40" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
              </span>
              Engine online
            </div>
          </header>

          <div className="mx-auto max-w-[1500px] px-10 py-10">
            {page === "dashboard" && (
              <Dashboard
                url={url}
                setUrl={setUrl}
                result={result}
                loading={loading}
                error={error}
                analyzeUrl={analyzeUrl}
                handleKeyDown={handleKeyDown}
                analysisStage={analysisStage}
                stages={stages}
              />
            )}

            {page === "scanner" && (
              <Dashboard
                url={url}
                setUrl={setUrl}
                result={result}
                loading={loading}
                error={error}
                analyzeUrl={analyzeUrl}
                handleKeyDown={handleKeyDown}
                analysisStage={analysisStage}
                stages={stages}
              />
            )}

            {page === "qr" && (
              <QRScanner
                onAnalyze={(decodedUrl) => analyzeUrl(decodedUrl)}
              />
            )}

            {page === "history" && (
              <HistoryPage
                history={history}
                onOpen={openHistoryItem}
                onClear={clearHistory}
              />
            )}

            {page === "model" && <ModelPage />}

            {page === "about" && <AboutPage />}
          </div>
        </main>
      </div>
    </div>
  );
}

/* ---------------- DASHBOARD ---------------- */

function Dashboard({
  url,
  setUrl,
  result,
  loading,
  error,
  analyzeUrl,
  handleKeyDown,
  analysisStage,
  stages,
}) {
  const isPhishing = result?.prediction === "phishing";
  const riskLevel = result?.risk_level;

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-[0_8px_30px_rgba(50,45,35,0.035)]">
        <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-normal tracking-tight text-[#111111]">
              Investigate a suspicious URL
            </h1>
          </div>

          <div className="inline-flex items-center gap-2 rounded-lg border border-[#D8D0C3] bg-[#F2EDE3] px-4 py-2 text-sm font-normal text-[#383431] self-start md:self-auto">
            Destination never loaded
          </div>
        </div>

        <div className="flex gap-4">
          <div className="flex min-h-[64px] flex-1 items-center rounded-xl border border-[#CFC7BA] bg-white/80 px-5 transition focus-within:border-[#2B2A29] focus-within:ring-4 focus-within:ring-[#2B2A29]/10 shadow-sm">
            <Globe2 size={22} className="mr-4 shrink-0 text-[#554F49]" />

            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              placeholder="https://example.com/login"
              className="w-full bg-transparent text-lg font-normal text-[#111111] outline-none placeholder:text-[#888077] disabled:cursor-not-allowed"
            />
          </div>

          <button
            onClick={() => analyzeUrl()}
            disabled={loading}
            className="flex min-h-[64px] min-w-[180px] items-center justify-center gap-3 rounded-xl bg-[#2B2A29] px-7 text-base font-normal text-white transition hover:bg-[#3D3B3A] disabled:cursor-not-allowed disabled:opacity-70 shadow-md"
          >
            {loading ? (
              <>
                <LoaderCircle size={20} className="animate-spin" />
                Analyzing
              </>
            ) : (
              <>
                <Search size={20} />
                Analyze URL
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-base font-normal text-red-700 shadow-sm">
            <AlertTriangle size={20} />
            {error}
          </div>
        )}

        <div className="mt-4 flex items-center gap-2 text-sm font-normal text-[#44403B]">
          URL structure only · destination is never loaded
        </div>
      </section>

      {loading && (
        <AnalysisPanel
          url={url}
          stage={analysisStage}
          stages={stages}
        />
      )}

      {result && !loading && (
        <ResultView
          result={result}
          isPhishing={isPhishing}
          riskLevel={riskLevel}
        />
      )}

      {!result && !loading && !error && (
        <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <InfoCard
            title="ML classification"
            text="A trained model evaluates overall URL feature characteristics."
          />

          <InfoCard
            title="Explainable signals"
            text="Suspicious patterns are highlighted alongside classification."
          />

          <InfoCard
            title="Safe inspection"
            text="Safely analyzes the exact string without live connections."
          />
        </section>
      )}
    </div>
  );
}

/* ---------------- RESULTS ---------------- */

function ResultView({ result, isPhishing, riskLevel }) {
  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
        <div className="mb-7">
          <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
            Investigation result
          </div>

          <h2 className="mt-2 text-3xl font-normal text-[#111111]">
            Threat assessment
          </h2>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-[#D8D0C3] bg-[#F2EDE3] p-8 shadow-sm">
            <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
              Risk score
            </div>

            <div className="mt-4 flex items-baseline gap-3">
              <span className="text-6xl font-normal tracking-tight text-[#111111]">
                {result.risk_score}
              </span>
              <span className="text-lg font-normal text-[#554F49]">
                / 100
              </span>
            </div>

            <div className="mt-3 text-lg font-normal text-[#111111]">
              {riskLevel} risk level detected
            </div>

            <div className="mt-5 h-3 overflow-hidden rounded-full bg-[#DDD5C8]">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  riskLevel === "HIGH"
                    ? "bg-red-500"
                    : riskLevel === "MEDIUM"
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                }`}
                style={{
                  width: `${Math.min(result.risk_score, 100)}%`,
                }}
              />
            </div>
          </div>

          <div className="rounded-2xl border border-[#D8D0C3] bg-[#F2EDE3] p-8 shadow-sm">
            <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
              Detection
            </div>

            <div className="mt-5">
              <div
                className={`text-4xl font-normal tracking-wide ${
                  isPhishing ? "text-red-600" : "text-emerald-600"
                }`}
              >
                {result.prediction.toUpperCase()}
              </div>

              <div className="mt-2 text-base font-normal text-[#44403B]">
                Machine-learning engine classification result
              </div>
            </div>

            <div className="mt-8 flex items-end justify-between border-t border-[#E2D9CC] pt-6">
              <div>
                <div className="text-sm font-normal uppercase text-[#554F49]">
                  Probability
                </div>
                <div className="mt-1 text-2xl font-normal text-[#111111]">
                  {result.phishing_probability}
                </div>
              </div>

              <div className="text-right">
                <div className="text-sm font-normal uppercase text-[#554F49]">
                  ML signals
                </div>
                <div className="mt-1 text-2xl font-normal text-[#111111]">
                  {result.signals_count}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-xl border border-[#D8D0C3] bg-white/50 px-6 py-4 shadow-sm">
          <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
            Analyzed target
          </div>
          <div className="mt-1.5 break-all font-mono text-base font-normal text-[#111111]">
            {result.url}
          </div>
        </div>
      </section>

      <section>
        <div className="mb-5 flex items-end justify-between">
          <div>
            <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
              Explainable detection
            </div>
            <h2 className="mt-1 text-2xl font-normal text-[#111111]">
              Security signals
            </h2>
          </div>

          <div className="text-base font-normal text-[#554F49]">
            {result.signals_count} detected
          </div>
        </div>

        {result.signals.length > 0 ? (
          <div className="overflow-hidden rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] shadow-sm">
            {result.signals.map((signal, index) => (
              <SignalRow key={index} signal={signal} />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
            <div className="text-lg font-normal text-[#111111]">
              No suspicious URL signals detected
            </div>
            <div className="mt-2 text-base font-normal text-[#44403B]">
              The URL structure did not trigger any configured security heuristics.
            </div>
          </div>
        )}
      </section>

      <section>
        <div className="mb-5">
          <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
            Structural inspection
          </div>
          <h2 className="mt-1 text-2xl font-normal text-[#111111]">
            URL telemetry
          </h2>
        </div>

        <div className="grid grid-cols-2 gap-5 md:grid-cols-4">
          <Telemetry
            label="HTTPS"
            value={result.features.has_https ? "Enabled" : "Disabled"}
          />
          <Telemetry
            label="SUBDOMAINS"
            value={result.features.num_subdomains}
          />
          <Telemetry
            label="URL LENGTH"
            value={`${result.features.url_length} chars`}
          />
          <Telemetry
            label="DOMAIN LENGTH"
            value={`${result.features.domain_length} chars`}
          />
        </div>
      </section>
    </div>
  );
}

/* ---------------- QR SCANNER ---------------- */

function QRScanner({ onAnalyze }) {
  const fileInputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [decodedUrl, setDecodedUrl] = useState("");
  const [qrError, setQrError] = useState("");
  const [scanning, setScanning] = useState(false);

  function handleFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setQrError("");
    setDecodedUrl("");
    setScanning(true);

    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.width = image.width;
        canvas.height = image.height;
        context.drawImage(image, 0, 0);

        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        setPreview(reader.result);
        setScanning(false);

        if (!code) {
          setQrError("No readable QR code was found in this image.");
          return;
        }
        setDecodedUrl(code.data);
      };
      image.onerror = () => {
        setScanning(false);
        setQrError("Unable to read the selected image.");
      };
      image.src = reader.result;
    };
    reader.readAsDataURL(file);
  }

  function reset() {
    setPreview(null);
    setDecodedUrl("");
    setQrError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <div>
      <PageHeading
        eyebrow="Secure QR inspection"
        title="QR Scanner"
        description="Upload a QR code image to safely inspect the destination URL."
      />

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
          <div>
            <h2 className="text-xl font-normal text-[#111111]">Scan QR image</h2>
            <p className="mt-2 text-base font-normal text-[#44403B]">
              QR decoding happens securely inside your browser.
            </p>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="mt-8 flex min-h-[190px] w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[#CFC7BA] bg-[#F2EDE3] transition hover:border-[#2B2A29] hover:bg-[#2B2A29]/[0.025]"
          >
            <div className="text-lg font-normal text-[#111111]">Upload QR image</div>
            <div className="mt-2 text-base font-normal text-[#554F49]">
              PNG, JPG or supported image formats
            </div>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFile}
            className="hidden"
          />

          {scanning && (
            <div className="mt-6 flex items-center gap-3 rounded-xl bg-[#2B2A29]/[0.06] px-5 py-4 text-base font-normal text-[#2B2A29]">
              <LoaderCircle size={20} className="animate-spin" />
              Reading QR code...
            </div>
          )}

          {qrError && (
            <div className="mt-6 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-base font-normal text-red-700">
              <AlertTriangle size={20} />
              {qrError}
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
          <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
            QR result
          </div>

          {preview ? (
            <div className="mt-6">
              <div className="flex justify-center rounded-xl bg-[#F2EDE3] p-6 shadow-sm">
                <img
                  src={preview}
                  alt="Uploaded QR"
                  className="max-h-56 rounded-lg object-contain"
                />
              </div>

              {decodedUrl && (
                <div className="mt-6">
                  <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
                    Decoded content
                  </div>
                  <div className="mt-2 break-all rounded-xl border border-[#D8D0C3] bg-[#F2EDE3] p-4 font-mono text-base font-normal text-[#111111]">
                    {decodedUrl}
                  </div>

                  <button
                    onClick={() => onAnalyze(decodedUrl)}
                    className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl bg-[#2B2A29] px-6 py-4 text-base font-normal text-white transition hover:bg-[#3D3B3A] shadow-md"
                  >
                    Analyze decoded URL
                  </button>
                </div>
              )}

              <button
                onClick={reset}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-[#CFC7BA] px-5 py-3 text-base font-normal text-[#38332F] transition hover:bg-[#F2EDE3]"
              >
                Clear scan
              </button>
            </div>
          ) : (
            <div className="flex min-h-[340px] flex-col items-center justify-center text-center">
              <div className="text-xl font-normal text-[#111111]">
                No QR code scanned
              </div>
              <div className="mt-2 max-w-sm text-base font-normal leading-relaxed text-[#554F49]">
                Upload a QR image to extract and evaluate any discovered URL.
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

/* ---------------- HISTORY ---------------- */

function HistoryPage({ history, onOpen, onClear }) {
  return (
    <div>
      <PageHeading
        eyebrow="Previous investigations"
        title="Analysis History"
        description="Review recent URL investigations stored locally on this device."
      />

      <div className="mt-8 rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] shadow-sm">
        <div className="flex items-center justify-between border-b border-[#D8D0C3] px-8 py-6">
          <div>
            <div className="text-lg font-normal text-[#111111]">Recent analyses</div>
            <div className="mt-1 text-base font-normal text-[#554F49]">
              {history.length} saved investigation{history.length === 1 ? "" : "s"}
            </div>
          </div>

          {history.length > 0 && (
            <button
              onClick={onClear}
              className="text-base font-normal text-red-600 hover:text-red-700"
            >
              Clear history
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <div className="flex min-h-[350px] flex-col items-center justify-center px-8 text-center">
            <div className="text-xl font-normal text-[#111111]">No analysis history</div>
            <div className="mt-2 max-w-md text-base font-normal leading-relaxed text-[#554F49]">
              URLs you analyze will appear here. History is stored securely in your browser's local storage.
            </div>
          </div>
        ) : (
          <div>
            {history.map((item) => (
              <button
                key={item.id}
                onClick={() => onOpen(item)}
                className="flex w-full items-center justify-between gap-6 border-b border-[#DED6C9] px-8 py-5 text-left transition last:border-b-0 hover:bg-[#F2EDE3]"
              >
                <div className="min-w-0">
                  <div className="truncate font-mono text-base font-normal text-[#111111]">
                    {item.url}
                  </div>
                  <div className="mt-2 flex items-center gap-3 text-sm font-normal text-[#554F49]">
                    <span>{formatDate(item.timestamp)}</span>
                    <span>·</span>
                    <span>{item.signals_count} signals</span>
                    <span>·</span>
                    <span>{item.phishing_probability} probability</span>
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-5">
                  <div
                    className={`rounded-full px-3.5 py-1.5 text-sm font-normal tracking-wide border ${
                      item.risk_level === "HIGH"
                        ? "bg-red-100 text-red-700 border-red-200"
                        : item.risk_level === "MEDIUM"
                          ? "bg-amber-100 text-amber-700 border-amber-200"
                          : "bg-emerald-100 text-emerald-700 border-emerald-200"
                    }`}
                  >
                    {item.risk_level}
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-normal text-[#111111]">
                      {item.risk_score}
                    </div>
                    <div className="text-sm font-normal uppercase text-[#554F49]">
                      risk
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------------- MODEL ---------------- */

function ModelPage() {
  return (
    <div>
      <PageHeading
        eyebrow="Detection engine"
        title="Model"
        description="Technical breakdown of the active PhishGuard machine learning architecture."
      />

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatCard label="Classifier" value="HistGradientBoosting" />
        <StatCard label="Features" value="37" />
        <StatCard label="Dataset" value="PhiUSIIL" />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
          <h2 className="text-2xl font-normal text-[#111111]">Analysis pipeline</h2>
          <div className="mt-6 space-y-4">
            <PipelineStep number="01" title="URL parsing" text="Extract structural and domain characteristics." />
            <PipelineStep number="02" title="Feature extraction" text="Build the 37-dimensional feature representation." />
            <PipelineStep number="03" title="ML classification" text="Run the trained gradient-boosting classifier." />
            <PipelineStep number="04" title="Security signals" text="Identify interpretable suspicious patterns." />
            <PipelineStep number="05" title="Risk assessment" text="Combine model output and security indicators." />
          </div>
        </section>

        <section className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
          <h2 className="text-2xl font-normal text-[#111111]">Feature groups</h2>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <FeatureGroup title="URL structure" items={["URL length", "Path length", "Query length", "Special characters"]} />
            <FeatureGroup title="Domain" items={["Subdomains", "Domain entropy", "Hyphens", "Numeric composition"]} />
            <FeatureGroup title="Security" items={["IP address", "HTTPS", "@ symbol", "URL encoding"]} />
            <FeatureGroup title="Keywords" items={["Login", "Verify", "Account", "Payment"]} />
          </div>
        </section>
      </div>

      <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-7 shadow-sm">
        <div className="text-lg font-normal text-amber-900">Important limitation</div>
        <p className="mt-2 text-base font-normal leading-relaxed text-amber-800">
          Model benchmark performance does not guarantee absolute real-world accuracy. URL structure alone cannot fully establish trustworthiness. PhishGuard is built as a decision-support tool.
        </p>
      </div>
    </div>
  );
}

/* ---------------- ABOUT ---------------- */

function AboutPage() {
  return (
    <div>
      <PageHeading
        eyebrow="Product information"
        title="About PhishGuard"
        description="A specialized URL intelligence tool for investigating potentially suspicious links."
      />

      <section className="mt-8 rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-8 shadow-sm">
        <h2 className="text-3xl font-normal text-[#111111]">PhishGuard Engine</h2>
        <p className="mt-3 max-w-3xl text-lg font-normal leading-relaxed text-[#44403B]">
          PhishGuard analyzes suspicious links using structural characteristics, machine learning classification, and explainable security signals. It helps security investigators understand why a URL deserves closer scrutiny.
        </p>
        <div className="mt-5 inline-flex items-center gap-2 rounded-full bg-[#2B2A29]/10 px-4 py-2 text-base font-normal text-[#2B2A29]">
          Version {VERSION}
        </div>
      </section>

      <section className="mt-8">
        <div className="mb-5">
          <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">Capabilities</div>
          <h2 className="mt-1 text-2xl font-normal text-[#111111]">Security analysis</h2>
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          <AboutCard title="URL structure" text="Length, paths, queries, special characters and encoding patterns." />
          <AboutCard title="Domain characteristics" text="Subdomains, domain composition, entropy, digits and hyphens." />
          <AboutCard title="Security indicators" text="IP-based URLs, HTTPS usage, suspicious symbols and patterns." />
          <AboutCard title="Keyword signals" text="Login, verification, account, security, update and payment terms." />
          <AboutCard title="Machine learning" text="A trained classifier evaluates the extracted URL feature representation." />
          <AboutCard title="Explainability" text="Security signals are surfaced directly alongside model classification." />
        </div>
      </section>
    </div>
  );
}

/* ---------------- ANALYSIS ANIMATION ---------------- */

function AnalysisPanel({ url, stage, stages }) {
  return (
    <section className="relative mt-8 overflow-hidden rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-9 shadow-[0_8px_30px_rgba(50,45,35,0.035)]">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-0 top-0 h-full w-1/3 animate-[scan_2.2s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-[#2B2A29]/[0.045] to-transparent" />
      </div>

      <div className="relative">
        <div className="flex flex-col items-center text-center">
          <div className="text-sm font-normal uppercase tracking-wider text-[#2B2A29]">
            Live analysis
          </div>

          <h2 className="mt-2 text-3xl font-normal tracking-tight text-[#111111]">
            Analyzing URL
          </h2>

          <p className="mt-2 text-lg font-normal text-[#44403B]">
            {stages[stage]}...
          </p>
        </div>

        <div className="mx-auto mt-7 max-w-3xl rounded-xl border border-[#D8D0C3] bg-[#F2EDE3] px-6 py-5 text-center shadow-sm">
          <div className="break-all font-mono text-base font-normal text-[#111111]">
            {url}
          </div>
        </div>

        <div className="mx-auto mt-7 max-w-3xl">
          <div className="mb-2.5 flex items-center justify-between text-base font-normal">
            <span className="text-[#38332F]">Security inspection</span>
            <span className="text-[#2B2A29]">
              {Math.round(((stage + 1) / stages.length) * 100)}%
            </span>
          </div>

          <div className="h-2.5 overflow-hidden rounded-full bg-[#DED6C9]">
            <div
              className="h-full rounded-full bg-[#2B2A29] transition-all duration-500"
              style={{
                width: `${((stage + 1) / stages.length) * 100}%`,
              }}
            />
          </div>
        </div>

        <div className="mx-auto mt-7 grid max-w-4xl grid-cols-1 gap-3 md:grid-cols-5">
          {stages.map((item, index) => {
            const completed = index < stage;
            const active = index === stage;

            return (
              <div
                key={item}
                className={`rounded-xl border px-4 py-3.5 transition-all duration-300 ${
                  completed
                    ? "border-[#2B2A29]/30 bg-[#2B2A29]/[0.05]"
                    : active
                      ? "border-[#2B2A29]/30 bg-[#2B2A29]/[0.055]"
                      : "border-[#D8D0C3] bg-[#F2EDE3]"
                }`}
              >
                <div className="flex items-center gap-3">
                  {completed ? (
                    <CheckCircle2 size={18} className="shrink-0 text-[#2B2A29]" />
                  ) : active ? (
                    <LoaderCircle size={18} className="shrink-0 animate-spin text-[#2B2A29]" />
                  ) : (
                    <Circle size={18} className="shrink-0 text-[#888077]" />
                  )}

                  <span
                    className={`text-sm font-normal ${
                      active
                        ? "text-[#2B2A29]"
                        : completed
                          ? "text-[#2B2A29]"
                          : "text-[#554F49]"
                    }`}
                  >
                    {item}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-7 flex items-center justify-center gap-2 text-base font-normal text-[#554F49]">
          Inspecting locally · destination is never loaded
        </div>
      </div>

      <style>{`
        @keyframes scan {
          0% { transform: translateX(-150%); }
          50% { transform: translateX(450%); }
          100% { transform: translateX(450%); }
        }
      `}</style>
    </section>
  );
}

/* ---------------- SHARED COMPONENTS ---------------- */

function NavSection({ label }) {
  return (
    <div className="mb-2 px-3 text-xs font-normal uppercase tracking-wider text-[#665E55]">
      {label}
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-3.5 rounded-xl px-4 py-3 text-left text-base font-normal transition ${
        active
          ? "bg-[#F2EDE3] text-[#2B2A29] shadow-sm"
          : "text-[#38332F] hover:bg-[#F2EDE3]/60"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

function PageHeading({ eyebrow, title, description }) {
  return (
    <div>
      <div className="text-sm font-normal uppercase tracking-wider text-[#2B2A29]">
        {eyebrow}
      </div>
      <h1 className="mt-1 text-3xl font-normal tracking-tight text-[#111111]">
        {title}
      </h1>
      <p className="mt-1.5 text-lg font-normal text-[#44403B]">
        {description}
      </p>
    </div>
  );
}

function SignalRow({ signal }) {
  return (
    <div className="flex gap-4 border-b border-[#DED6C9] px-8 py-5 last:border-b-0">
      <div>
        <div className="text-lg font-normal text-[#111111]">
          {signal.title}
        </div>
        <div className="mt-1 text-base font-normal leading-relaxed text-[#44403B]">
          {signal.description}
        </div>
      </div>
    </div>
  );
}

function Telemetry({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-6 shadow-sm">
      <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
        {label}
      </div>
      <div className="mt-2.5 text-xl font-normal text-[#111111]">
        {value}
      </div>
    </div>
  );
}

function InfoCard({ title, text }) {
  return (
    <div className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-7 shadow-sm">
      <div className="text-xl font-normal text-[#111111]">
        {title}
      </div>
      <p className="mt-2 text-base font-normal leading-relaxed text-[#44403B]">
        {text}
      </p>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-7 shadow-sm">
      <div className="text-sm font-normal uppercase tracking-wider text-[#554F49]">
        {label}
      </div>
      <div className="mt-2.5 text-xl font-normal text-[#111111]">
        {value}
      </div>
    </div>
  );
}

function PipelineStep({ number, title, text }) {
  return (
    <div className="flex gap-4 rounded-xl border border-[#D8D0C3] bg-[#F2EDE3] p-4 shadow-sm">
      <div className="font-mono text-base font-normal text-[#2B2A29]">
        {number}
      </div>
      <div>
        <div className="text-base font-normal text-[#111111]">{title}</div>
        <div className="mt-1 text-sm font-normal text-[#44403B]">
          {text}
        </div>
      </div>
    </div>
  );
}

function FeatureGroup({ title, items }) {
  return (
    <div className="rounded-xl border border-[#D8D0C3] bg-[#F2EDE3] p-5 shadow-sm">
      <div className="text-base font-normal text-[#111111]">{title}</div>
      <div className="mt-3 space-y-2">
        {items.map((item) => (
          <div
            key={item}
            className="flex items-center gap-2.5 text-sm font-normal text-[#44403B]"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-[#2B2A29]" />
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

function AboutCard({ title, text }) {
  return (
    <div className="rounded-2xl border border-[#D8D0C3] bg-[#FAF7F0] p-7 shadow-sm">
      <div className="text-xl font-normal text-[#111111]">
        {title}
      </div>
      <p className="mt-2 text-base font-normal leading-relaxed text-[#44403B]">
        {text}
      </p>
    </div>
  );
}

function pageTitle(page) {
  const titles = {
    dashboard: "URL Analysis",
    scanner: "URL Scanner",
    qr: "QR Scanner",
    history: "Analysis History",
    model: "Detection Model",
    about: "About PhishGuard",
  };

  return titles[page] || "URL Analysis";
}

function formatDate(timestamp) {
  try {
    return new Date(timestamp).toLocaleString();
  } catch {
    return "Unknown date";
  }
}

export default App;
