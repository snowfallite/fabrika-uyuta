<script lang="ts">
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { WORKS } from '$lib/content/home';
	import { PRODUCT_KIND_LABELS } from '$lib/domain/product-kind';
	import type { GalleryItem } from '$lib/types';
	import Lightbox from './Lightbox.svelte';

	interface Props {
		items: GalleryItem[];
		id?: string;
		title?: string;
		subtitle?: string;
		tone?: 'default' | 'muted';
	}

	let {
		items,
		id = 'works',
		title = WORKS.title,
		subtitle = WORKS.eyebrow,
		tone = 'default'
	}: Props = $props();

	let open = $state(false);
	let index = $state(0);

	// A grid reads left to right in admin order; two columns for 2 or 4 works leave no hole.
	const columns = $derived(
		items.length === 1
			? 'max-w-3xl'
			: items.length === 2 || items.length === 4
				? 'sm:grid-cols-2'
				: 'sm:grid-cols-2 lg:grid-cols-3'
	);

	function show(event: MouseEvent, position: number) {
		if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey) return;
		// Without JS the link opens the widest variant itself.
		event.preventDefault();
		index = position;
		open = true;
	}
</script>

<Section {id} {title} {subtitle} {tone}>
	<ul class="grid gap-4 md:gap-6 {columns}">
		{#each items as item, position (item.id)}
			<li>
				<a
					href={item.image.url}
					class="group relative block aspect-[4/3] lift-hover overflow-hidden rounded-[1.5rem] bg-card"
					onclick={(event) => show(event, position)}
				>
					<ResponsiveImage
						image={item.image}
						sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
						class="size-full object-cover transition-transform duration-700 group-hover:scale-[1.04]"
					/>
					<span
						class="absolute inset-0 bg-linear-to-t from-primary/90 via-primary/10 to-transparent"
						aria-hidden="true"
					></span>
					<span class="absolute inset-x-0 bottom-0 p-5 text-left">
						<span class="block text-xs tracking-widest text-primary-foreground uppercase">
							{PRODUCT_KIND_LABELS[item.category]}
						</span>
						<span class="block font-display text-xl text-primary-foreground">
							{item.title || WORKS.photoTitle}
						</span>
					</span>
				</a>
			</li>
		{/each}
	</ul>
</Section>

<Lightbox {items} bind:open bind:index />
