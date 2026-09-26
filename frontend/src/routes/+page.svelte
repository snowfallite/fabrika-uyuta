<script lang="ts">
	import { env } from '$env/dynamic/public';
	import Seo from '$lib/components/layout/Seo.svelte';
	import { HOME_SEO } from '$lib/content/pages';
	import { furnitureStoreJsonLd, jsonLdScript } from '$lib/domain/json-ld';
	import CategoryGrid from '$lib/features/categories/CategoryGrid.svelte';
	import GalleryGrid from '$lib/features/gallery/GalleryGrid.svelte';
	import Hero from '$lib/features/hero/Hero.svelte';
	import LeadSection from '$lib/features/lead-form/LeadSection.svelte';
	import About from '$lib/features/sections/About.svelte';
	import Advantages from '$lib/features/sections/Advantages.svelte';
	import Contacts from '$lib/features/sections/Contacts.svelte';
	import Materials from '$lib/features/sections/Materials.svelte';
	import Process from '$lib/features/sections/Process.svelte';

	let { data } = $props();

	const jsonLd = $derived(
		furnitureStoreJsonLd(env.PUBLIC_SITE_URL ?? '', data.settings, data.home.slots.hero)
	);
</script>

<Seo
	title={HOME_SEO.title}
	description={HOME_SEO.description}
	path="/"
	image={data.home.slots.hero}
/>
<svelte:head>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -- escaped JSON built in json-ld.ts -->
	{@html jsonLdScript(jsonLd)}
</svelte:head>

<!-- Section order follows the template (tech.md, appendix A). -->
<Hero image={data.home.slots.hero} />
<About image={data.home.slots.about} />
<CategoryGrid categories={data.home.categories} />
{#if data.home.featured.length > 0}
	<GalleryGrid items={data.home.featured} />
{/if}
<Materials slots={data.home.slots} />
<Process />
<Advantages />
<LeadSection settings={data.settings} />
<Contacts settings={data.settings} />
