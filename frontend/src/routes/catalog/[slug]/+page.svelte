<script lang="ts">
	import { env } from '$env/dynamic/public';
	import Seo from '$lib/components/layout/Seo.svelte';
	import { CATEGORY_PAGE } from '$lib/content/pages';
	import { breadcrumbListJsonLd, jsonLdScript } from '$lib/domain/json-ld';
	import CategoryPage from '$lib/features/category-page/CategoryPage.svelte';
	import { categoryCrumbs } from '$lib/features/category-page/crumbs';

	let { data } = $props();

	const crumbs = $derived(
		breadcrumbListJsonLd(env.PUBLIC_SITE_URL ?? '', categoryCrumbs(data.category.title))
	);
</script>

<Seo
	title={data.category.seo_title + CATEGORY_PAGE.titleSuffix}
	description={data.category.seo_description}
	path="/catalog/{data.category.slug}"
	image={data.category.cover}
/>
<svelte:head>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -- escaped JSON built in json-ld.ts -->
	{@html jsonLdScript(crumbs)}
</svelte:head>

<CategoryPage category={data.category} settings={data.settings} />
