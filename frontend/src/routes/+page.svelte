<script lang="ts">
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
<LeadSection settings={data.settings} />
