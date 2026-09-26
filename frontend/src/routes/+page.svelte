<script lang="ts">
	import CategoryGrid from '$lib/features/categories/CategoryGrid.svelte';
	import GalleryGrid from '$lib/features/gallery/GalleryGrid.svelte';
	import Hero from '$lib/features/hero/Hero.svelte';
	import LeadSection from '$lib/features/lead-form/LeadSection.svelte';

	let { data } = $props();
</script>

<svelte:head>
	<title>Фабрика Уюта: мебель на заказ в Вологде</title>
	<meta
		name="description"
		content="Кухни, шкафы, шкафы-купе, кухонные столы и офисная мебель на заказ в Вологде. ЛДСП и МДФ."
	/>
</svelte:head>

<Hero image={data.home.slots.hero} />
<CategoryGrid categories={data.home.categories} />
{#if data.home.featured.length > 0}
	<GalleryGrid items={data.home.featured} />
{/if}
<LeadSection settings={data.settings} />
