/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CTRADER_MCP_URL: string
  readonly VITE_CTRADER_MCP_TOKEN: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
