import {Config} from '@remotion/cli/config';

// Linux / ARM (e.g. Raspberry Pi) support.
// Chrome-for-Testing has no linux-arm64 build, so Remotion can't download a browser there.
// Point it at a system Chromium via env, e.g.:
//   export REMOTION_BROWSER_EXECUTABLE=/usr/bin/chromium
// On a GPU-less headless box also set software GL (default 'swangle'); override with REMOTION_GL.
// Both are unset on macOS / x86 → this file is a no-op and Remotion uses its own browser.
const browser = process.env.REMOTION_BROWSER_EXECUTABLE;
if (browser) {
  Config.setBrowserExecutable(browser);
  Config.setChromiumOpenGlRenderer((process.env.REMOTION_GL as never) || 'swangle');
}
