import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Runes everywhere except dependencies; drop with Svelte 6.
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter(),
		// One foreign script: the Yandex.Metrika counter (tech.md, 10.2 and 13.2).
		csp: {
			mode: 'auto',
			directives: {
				'default-src': ['self'],
				'script-src': ['self', 'https://mc.yandex.ru'],
				'img-src': ['self', 'data:', 'https://mc.yandex.ru'],
				'font-src': ['self'],
				'style-src': ['self', 'unsafe-inline'],
				'connect-src': ['self', 'https://mc.yandex.ru'],
				'frame-ancestors': ['none'],
				'form-action': ['self'],
				'base-uri': ['self']
			}
		}
	}
};

export default config;
