<script lang="ts">
	import '../app.css';
	import Footer from '$lib/components/layout/Footer.svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import SkipLink from '$lib/components/layout/SkipLink.svelte';
	import { NAV } from '$lib/config/nav';

	let { data, children } = $props();
</script>

<SkipLink />
<Header settings={data.settings} nav={NAV} />
<main id="main" tabindex="-1" class="outline-none">
	{@render children()}
</main>
<Footer settings={data.settings} nav={NAV} />
