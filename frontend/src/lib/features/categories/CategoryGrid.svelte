<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { CATALOG } from '$lib/content/home';
	import type { CategorySummary } from '$lib/types';
	import CategoryCard from './CategoryCard.svelte';

	interface Props {
		categories: CategorySummary[];
	}

	let { categories }: Props = $props();

	// Six tracks on desktop: two wide cards over three narrow ones, so five categories fill
	// the grid without a hole. On two columns an odd last card spans the whole row.
	function placement(index: number, count: number) {
		const wide = count === 5 && index < 2;
		const lastOdd = index === count - 1 && count % 2 === 1;
		return [
			wide ? 'lg:col-span-3 lg:aspect-[3/2]' : 'lg:col-span-2 lg:aspect-[4/5]',
			lastOdd ? 'sm:col-span-2 sm:aspect-[2/1]' : ''
		].join(' ');
	}
</script>

<Section id="catalog" title={CATALOG.title} subtitle={CATALOG.eyebrow} tone="muted">
	<p class="-mt-4 mb-8 max-w-md leading-relaxed text-muted-foreground md:mb-10">{CATALOG.text}</p>
	<div class="grid gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-6">
		{#each categories as category, index (category.slug)}
			<CategoryCard {category} class={placement(index, categories.length)} />
		{/each}
	</div>
</Section>
