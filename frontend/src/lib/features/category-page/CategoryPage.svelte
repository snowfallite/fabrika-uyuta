<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import { Container } from '$lib/components/ui/container';
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { CATEGORY_PAGE } from '$lib/content/pages';
	import { splitParagraphs } from '$lib/domain/text';
	import GalleryGrid from '$lib/features/gallery/GalleryGrid.svelte';
	import LeadSection from '$lib/features/lead-form/LeadSection.svelte';
	import type { CategoryDetail, SiteSettings } from '$lib/types';

	interface Props {
		category: CategoryDetail;
		settings: SiteSettings;
	}

	let { category, settings }: Props = $props();

	const paragraphs = $derived(splitParagraphs(category.description));
</script>

<Container class="pt-24 pb-12 md:pt-28">
	<a
		href="/#catalog"
		class="inline-flex items-center gap-2 py-3 text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
	>
		<ArrowLeft class="size-4" aria-hidden="true" />{CATEGORY_PAGE.back}
	</a>
	<div class="mt-4 grid items-center gap-8 lg:grid-cols-12 lg:gap-12">
		<div class="lg:col-span-6">
			<h1 class="text-display">
				{category.title}
			</h1>
			{#if category.short_description}
				<p class="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">
					{category.short_description}
				</p>
			{/if}
			{#if paragraphs.length > 0}
				<div
					class="mt-6 max-w-xl space-y-4 leading-relaxed text-foreground/85"
					data-testid="description"
				>
					{#each paragraphs as paragraph, index (index)}
						<p class="whitespace-pre-line">{paragraph}</p>
					{/each}
				</div>
			{/if}
		</div>
		<div class="order-first lg:order-last lg:col-span-6">
			<div class="aspect-[4/3] overflow-hidden rounded-[2rem] sm:aspect-[16/10] lg:aspect-[4/5]">
				<ResponsiveImage
					image={category.cover}
					sizes="(min-width: 1024px) 50vw, 100vw"
					loading="eager"
					fetchpriority="high"
					class="size-full object-cover"
				/>
			</div>
		</div>
	</div>
</Container>

{#if category.gallery.length > 0}
	<GalleryGrid
		items={category.gallery}
		id="category-works"
		title={CATEGORY_PAGE.worksTitle}
		subtitle={category.title}
		tone="muted"
	/>
{:else}
	<Section id="category-works" title={CATEGORY_PAGE.worksTitle} tone="muted">
		<p class="text-muted-foreground">{CATEGORY_PAGE.emptyGallery}</p>
	</Section>
{/if}

<LeadSection id="category-lead" idPrefix="category" product={category.slug} {settings} />
