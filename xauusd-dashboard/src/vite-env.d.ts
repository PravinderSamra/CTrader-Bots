/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CTRADER_MCP_URL: string
  readonly VITE_CTRADER_MCP_TOKEN: string
  readonly VITE_FINNHUB_KEY: string
  readonly VITE_ANTHROPIC_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
