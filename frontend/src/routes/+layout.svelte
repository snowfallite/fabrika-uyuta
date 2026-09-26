<script lang="ts">
	import '../app.css';
	import { navigating } from '$app/state';
	import Footer from '$lib/components/layout/Footer.svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import SkipLink from '$lib/components/layout/SkipLink.svelte';
	import { NAV } from '$lib/config/nav';
	import LeadDialog from '$lib/features/lead-form/LeadDialog.svelte';

	let { data, children } = $props();
</script>

{#if navigating.to}
	<!-- Page data loads on the server; the bar shows a slow transition is under way. -->
	<div class="fixed inset-x-0 top-0 z-[60] h-0.5 animate-pulse bg-primary" aria-hidden="true"></div>
{/if}
<SkipLink />
<div class="flex min-h-dvh flex-col">
	<Header settings={data.settings} nav={NAV} />
	<main id="main" tabindex="-1" class="flex-1 outline-none">
		{@render children()}
	</main>
	<Footer settings={data.settings} nav={NAV} />
</div>
<LeadDialog settings={data.settings} />
