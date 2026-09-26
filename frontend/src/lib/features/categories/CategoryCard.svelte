<script lang="ts">
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { CATALOG } from '$lib/content/home';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import type { CategorySummary } from '$lib/types';

	interface Props {
		category: CategorySummary;
	}

	let { category }: Props = $props();
</script>

<article
	class="group relative aspect-[4/5] lift-hover overflow-hidden rounded-[1.75rem] bg-card has-[h3_a:focus-visible]:outline-2 has-[h3_a:focus-visible]:outline-offset-3 has-[h3_a:focus-visible]:outline-ring"
>
	<ResponsiveImage
		image={category.cover}
		sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
		aspect="4/5"
		class="size-full object-cover transition-transform duration-700 group-hover:scale-105"
	/>
	<div
		class="absolute inset-0 bg-linear-to-t from-primary/90 via-primary/20 to-transparent"
		aria-hidden="true"
	></div>
	<div class="absolute inset-0 flex flex-col justify-end gap-4 p-6">
		<div>
			<h3 class="text-2xl text-primary-foreground">
				<!-- The link covers the whole card; the CTA sits above it. -->
				<a href="/catalog/{category.slug}" class="outline-none after:absolute after:inset-0"
					>{category.title}</a
				>
			</h3>
			{#if category.short_description}
				<p
					class="mt-2 text-sm leading-relaxed text-primary-foreground transition-all duration-500 lg:max-h-0 lg:overflow-hidden lg:opacity-0 lg:group-focus-within:max-h-32 lg:group-focus-within:opacity-100 lg:group-hover:max-h-32 lg:group-hover:opacity-100"
				>
					{category.short_description}
				</p>
			{/if}
		</div>
		<a
			href="/lead?product={category.slug}"
			class="relative z-10 inline-flex w-fit items-center rounded-full px-5 py-2.5 text-sm font-medium text-primary glass transition-colors hover:bg-secondary/80 focus-visible:outline-primary-foreground"
			onclick={(event) => openFromLink(event, category.slug)}
		>
			{CATALOG.cardCta}
		</a>
	</div>
</article>
