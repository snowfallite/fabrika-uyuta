<script lang="ts">
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import { Container } from '$lib/components/ui/container';
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { LEAD_SECTION } from '$lib/content/lead-form';
	import { CATEGORY_PAGE } from '$lib/content/pages';
	import { splitParagraphs } from '$lib/domain/text';
	import GalleryGrid from '$lib/features/gallery/GalleryGrid.svelte';
	import LeadForm from '$lib/features/lead-form/LeadForm.svelte';
	import type { CategoryDetail, SiteSettings } from '$lib/types';

	interface Props {
		category: CategoryDetail;
		settings: SiteSettings;
	}

	let { category, settings }: Props = $props();

	const paragraphs = $derived(splitParagraphs(category.description));
</script>

<Container class="pt-32 pb-16 md:pt-36">
	<a
		href="/#catalog"
		class="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
	>
		<ArrowLeft class="size-4" aria-hidden="true" />{CATEGORY_PAGE.back}
	</a>
	<div class="mt-8 grid items-center gap-10 lg:grid-cols-12 lg:gap-12">
		<div class="lg:col-span-6">
			<h1
				class="text-[2.75rem] leading-[1.05] font-light text-balance text-primary sm:text-6xl lg:text-[4.5rem]"
			>
				{category.title}
			</h1>
			{#if category.short_description}
				<p class="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
					{category.short_description}
				</p>
			{/if}
			{#if paragraphs.length > 0}
				<div
					class="mt-8 max-w-xl space-y-4 leading-relaxed text-foreground/85"
					data-testid="description"
				>
					{#each paragraphs as paragraph, index (index)}
						<p class="whitespace-pre-line">{paragraph}</p>
					{/each}
				</div>
			{/if}
		</div>
		<div class="lg:col-span-6">
			<div class="aspect-[4/5] overflow-hidden rounded-[2rem] sm:aspect-[5/4] lg:aspect-[4/5]">
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

<Section id="category-lead" title={LEAD_SECTION.title} subtitle={LEAD_SECTION.eyebrow}>
	<div class="grid gap-10 lg:grid-cols-2 lg:gap-16">
		<p class="max-w-md text-lg leading-relaxed text-muted-foreground">{LEAD_SECTION.text}</p>
		<div class="rounded-[2rem] p-7 glass md:p-10">
			<LeadForm
				idPrefix="category"
				product={category.slug}
				phone={settings.phone}
				phoneDisplay={settings.phone_display}
			/>
		</div>
	</div>
</Section>
