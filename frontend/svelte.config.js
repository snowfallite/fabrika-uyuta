import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Runes everywhere except dependencies; drop with Svelte 6.
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter(),
		// No foreign scripts, fonts or widgets (tech.md, 10.2 and 13.2).
		csp: {
			mode: 'auto',
			directives: {
				'default-src': ['self'],
				'script-src': ['self'],
				'img-src': ['self', 'data:'],
				'font-src': ['self'],
				'style-src': ['self', 'unsafe-inline'],
				'connect-src': ['self'],
				'frame-ancestors': ['none'],
				'form-action': ['self'],
				'base-uri': ['self']
			}
		}
	}
};

export default config;
