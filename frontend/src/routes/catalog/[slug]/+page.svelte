<script lang="ts">
	import Seo from '$lib/components/layout/Seo.svelte';
	import { CATEGORY_PAGE } from '$lib/content/pages';
	import CategoryPage from '$lib/features/category-page/CategoryPage.svelte';

	let { data } = $props();
</script>

<Seo
	title={data.category.seo_title + CATEGORY_PAGE.titleSuffix}
	description={data.category.seo_description}
	path="/catalog/{data.category.slug}"
	image={data.category.cover}
/>

<CategoryPage category={data.category} settings={data.settings} />
