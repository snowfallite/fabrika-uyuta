<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { CATALOG } from '$lib/content/home';
	import type { CategorySummary } from '$lib/types';
	import CategoryCard from './CategoryCard.svelte';

	interface Props {
		categories: CategorySummary[];
	}

	let { categories }: Props = $props();
</script>

<Section id="catalog" title={CATALOG.title} subtitle={CATALOG.eyebrow} tone="muted">
	<p class="-mt-6 mb-12 max-w-md leading-relaxed text-muted-foreground">{CATALOG.text}</p>
	<div class="grid gap-5 sm:grid-cols-2 md:gap-7 lg:grid-cols-3">
		{#each categories as category (category.slug)}
			<CategoryCard {category} />
		{/each}
	</div>
</Section>
