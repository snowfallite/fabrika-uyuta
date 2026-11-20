<script lang="ts">
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { CATALOG } from '$lib/content/home';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import type { CategorySummary } from '$lib/types';
	import { cn } from '$lib/utils';

	interface Props {
		category: CategorySummary;
		/** Grid placement, set by CategoryGrid. */
		class?: string;
		/** Aspect of the photo below lg, where the text sits under it. */
		coverClass?: string;
	}

	let { category, class: className, coverClass }: Props = $props();
</script>

<!--
  Up to lg the text sits under the photo: a touch screen has no hover to reveal
  the description, so it covered the photo in white copy nobody could read.
  From lg the card keeps the overlay and reveals the description on hover.
-->
<article
	class={cn(
		'group relative flex lift-hover flex-col overflow-hidden rounded-[1.75rem] bg-card has-[h3_a:focus-visible]:outline-2 has-[h3_a:focus-visible]:outline-offset-3 has-[h3_a:focus-visible]:outline-ring lg:block',
		className
	)}
>
	<div
		class={cn(
			'relative aspect-[4/3] overflow-hidden lg:absolute lg:inset-0 lg:aspect-auto',
			coverClass
		)}
	>
		<ResponsiveImage
			image={category.cover}
			sizes="(min-width: 1024px) 50vw, (min-width: 640px) 50vw, 100vw"
			class="size-full object-cover transition-transform duration-700 group-hover:scale-105"
		/>
		<div
			class="absolute inset-0 hidden bg-linear-to-t from-primary/90 via-primary/20 to-transparent lg:block"
			aria-hidden="true"
		></div>
	</div>
	<div class="flex grow flex-col gap-4 p-5 sm:p-6 lg:absolute lg:inset-0 lg:justify-end lg:p-6">
		<div>
			<h3 class="text-2xl text-foreground lg:text-primary-foreground">
				<!-- The link covers the whole card; the CTA sits above it. -->
				<a href="/catalog/{category.slug}" class="outline-none after:absolute after:inset-0"
					>{category.title}</a
				>
			</h3>
			{#if category.short_description}
				<p
					class="mt-2 text-sm leading-relaxed text-muted-foreground transition-all duration-500 lg:max-h-0 lg:overflow-hidden lg:text-primary-foreground lg:opacity-0 lg:group-focus-within:max-h-32 lg:group-focus-within:opacity-100 lg:group-hover:max-h-32 lg:group-hover:opacity-100"
				>
					{category.short_description}
				</p>
			{/if}
		</div>
		<a
			href="/lead?product={category.slug}"
			class="relative z-10 mt-auto inline-flex w-fit items-center rounded-full bg-secondary px-5 py-2.5 text-sm font-medium text-secondary-foreground transition-colors hover:bg-secondary/80 lg:mt-0 lg:text-primary lg:glass lg:hover:bg-secondary/80 lg:focus-visible:outline-primary-foreground"
			onclick={(event) => openFromLink(event, category.slug)}
		>
			{CATALOG.cardCta}
		</a>
	</div>
</article>
