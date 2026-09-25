<script lang="ts">
	import type { ImageAsset } from '$lib/types';
	import { cn } from '$lib/utils.js';

	interface Props {
		image: ImageAsset | null;
		sizes: string;
		loading?: 'lazy' | 'eager';
		fetchpriority?: 'high' | 'auto';
		/** CSS aspect-ratio of the empty placeholder. */
		aspect?: string;
		class?: string;
	}

	let { image, sizes, loading = 'lazy', fetchpriority, aspect, class: className }: Props = $props();
</script>

{#if image}
	<img
		src={image.url}
		srcset={image.srcset}
		{sizes}
		width={image.width}
		height={image.height}
		alt={image.alt}
		{loading}
		{fetchpriority}
		decoding="async"
		class={className}
		style:background-color={image.color}
	/>
{:else}
	<div
		aria-hidden="true"
		class={cn('bg-linear-to-br from-secondary via-muted to-primary/30', className)}
		style:aspect-ratio={aspect}
	></div>
{/if}
