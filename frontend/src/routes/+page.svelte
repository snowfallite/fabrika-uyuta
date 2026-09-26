<script lang="ts">
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
</script>

<svelte:head>
	<title>Фабрика Уюта: мебель на заказ в Вологде</title>
	<meta
		name="description"
		content="Кухни, шкафы, шкафы-купе, кухонные столы и офисная мебель на заказ в Вологде. ЛДСП и МДФ."
	/>
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
