<script lang="ts">
	import ChevronLeft from '@lucide/svelte/icons/chevron-left';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import X from '@lucide/svelte/icons/x';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import { WORKS } from '$lib/content/home';
	import type { GalleryItem } from '$lib/types';
	import { nextIndex } from './gallery';

	interface Props {
		items: GalleryItem[];
		open: boolean;
		index: number;
	}

	let { items, open = $bindable(), index = $bindable() }: Props = $props();

	const current = $derived(items[index]);
	const step = (direction: 1 | -1) => (index = nextIndex(index, items.length, direction));

	function onkeydown(event: KeyboardEvent) {
		if (event.key === 'ArrowRight') step(1);
		if (event.key === 'ArrowLeft') step(-1);
	}
</script>

<Dialog.Root bind:open>
	<!-- Full-screen dark stage from the template; the controls are glass on it. -->
	<Dialog.Content
		showCloseButton={false}
		class="top-0 left-0 flex h-dvh max-h-none w-full max-w-none translate-x-0 translate-y-0 items-center justify-center rounded-none bg-primary/85 p-4 shadow-none backdrop-blur-xl sm:max-w-none md:p-10 [&_:focus-visible]:outline-primary-foreground"
		{onkeydown}
	>
		{#if current}
			<figure class="flex max-h-full w-full max-w-5xl flex-col items-center">
				<img
					src={current.image.url}
					alt={current.image.alt}
					width={current.image.width}
					height={current.image.height}
					class="max-h-[75dvh] w-auto rounded-2xl object-contain"
					style:background-color={current.image.color}
				/>
				<figcaption class="mt-5 text-center text-primary-foreground">
					<span class="block text-xs tracking-widest uppercase">
						{current.category_title}{#if items.length > 1}<span class="ml-3 tabular-nums"
								>{index + 1} / {items.length}</span
							>{/if}
					</span>
					<Dialog.Title class="text-2xl text-primary-foreground">
						{current.title || WORKS.photoTitle}
					</Dialog.Title>
					{#if current.caption}
						<Dialog.Description class="mt-1 text-sm text-primary-foreground"
							>{current.caption}</Dialog.Description
						>
					{/if}
				</figcaption>
			</figure>
		{/if}
		{#if items.length > 1}
			<Button
				variant="ghost"
				size="icon"
				class="absolute top-1/2 left-3 -translate-y-1/2 text-primary-foreground glass-dark md:left-6"
				aria-label={WORKS.previous}
				onclick={() => step(-1)}
			>
				<ChevronLeft class="size-6" aria-hidden="true" />
			</Button>
			<Button
				variant="ghost"
				size="icon"
				class="absolute top-1/2 right-3 -translate-y-1/2 text-primary-foreground glass-dark md:right-6"
				aria-label={WORKS.next}
				onclick={() => step(1)}
			>
				<ChevronRight class="size-6" aria-hidden="true" />
			</Button>
		{/if}
		<Dialog.Close
			class="absolute top-5 right-5 inline-flex size-11 items-center justify-center rounded-full text-primary-foreground glass-dark"
			aria-label={WORKS.close}
		>
			<X class="size-5" aria-hidden="true" />
		</Dialog.Close>
	</Dialog.Content>
</Dialog.Root>
