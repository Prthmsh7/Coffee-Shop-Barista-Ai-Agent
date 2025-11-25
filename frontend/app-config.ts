export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Ember & Oak Coffeehouse',
  pageTitle: 'Ember & Oak Virtual Barista',
  pageDescription: 'Chat with Ember, your vintage coffee shop barista, and place a handcrafted order.',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#8c4b2b',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#f1c49d',
  startButtonText: 'Order with Ember',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
