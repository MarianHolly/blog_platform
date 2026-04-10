// @ts-check
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	site: 'http://localhost:4321',
	output: 'hybrid',
	integrations: [sitemap()],
	vite: {
		plugins: [tailwindcss()],
	},
});
