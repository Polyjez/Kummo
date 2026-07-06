/**
 * Kummo environment configuration
 *
 * Environment is selected via the start script:
 *   ./start-kummo.sh [env]
 *
 * The script reads .env.<env> and writes js/env.js which sets
 * window.KummoEnv with the Supabase URL and anon key.
 *
 * js/env.js is required — the app will not connect without it.
 */
(function () {
  'use strict';

  var env = window.KummoEnv;

  if (!env || !env.supabaseUrl || !env.supabaseAnonKey) {
    console.error(
      'Kummo: js/env.js is missing or incomplete. ' +
      'Start the app with: ./start-kummo.sh [env]'
    );
  }

  window.KummoConfig = {
    supabaseUrl: env ? env.supabaseUrl : '',
    supabaseAnonKey: env ? env.supabaseAnonKey : ''
  };
})();
