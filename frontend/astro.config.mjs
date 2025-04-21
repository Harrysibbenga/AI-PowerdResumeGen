import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from "@astrojs/tailwind";
import path from 'path';

export default defineConfig({
  integrations: [tailwind(), vue()],
  vite: {
    resolve: {
      alias: {
        '@': path.resolve('./src'),
      },
    },
  },
});
