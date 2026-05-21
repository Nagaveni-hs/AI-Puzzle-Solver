import { spawn } from "child_process";

console.log("Starting Streamlit app...");

const streamlit = spawn("streamlit", ["run", "app.py",
  "--server.port", "5000", "--server.address", "0.0.0.0"], {
  stdio: "inherit",
  shell: true
});

streamlit.on("close", (code) => {
  console.log(`Streamlit exited with code ${code}`);
  process.exit(code ?? 0);
});

const cleanup = () => { streamlit.kill(); process.exit(0); };
process.on("SIGTERM", cleanup);
process.on("SIGINT",  cleanup);