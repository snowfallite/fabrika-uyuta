<script lang="ts">
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { Button } from '$lib/components/ui/button';
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { HERO } from '$lib/content/home';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import type { ImageAsset } from '$lib/types';

	interface Props {
		image: ImageAsset | null;
	}

	let { image }: Props = $props();
</script>

<Section
	id="hero"
	class="relative flex items-center pt-24 pb-10 md:pt-28 lg:min-h-[100svh] lg:pb-16"
>
	<div class="grid items-center gap-8 lg:grid-cols-12 lg:gap-12">
		<!-- On phones the photo comes first: the first screen shows the furniture, not only text. -->
		<div class="relative order-first lg:order-last lg:col-span-6">
			<div
				class="relative aspect-[4/3] overflow-hidden rounded-[2rem] sm:aspect-[16/10] lg:aspect-[4/5]"
			>
				<!-- The LCP element: eager and high priority (tech.md, S1-09). -->
				<ResponsiveImage
					{image}
					sizes="(min-width: 1024px) 50vw, 100vw"
					loading="eager"
					fetchpriority="high"
					class="size-full object-cover"
				/>
				<div
					class="absolute inset-0 bg-linear-to-t from-primary/25 via-transparent to-transparent"
				></div>
			</div>
		</div>
		<div class="z-10 lg:col-span-6">
			<h1
				class="text-[2.75rem] leading-[1.05] font-light text-balance text-primary sm:text-6xl lg:text-[5rem]"
			>
				{HERO.title}
			</h1>
			<p class="mt-5 max-w-xl text-lg leading-relaxed text-muted-foreground">{HERO.subtitle}</p>
			<div class="mt-8 flex flex-col gap-3 sm:flex-row">
				<Button href="/lead" onclick={(event: MouseEvent) => openFromLink(event)}>
					{HERO.cta}
					<ArrowRight
						class="transition-transform group-hover/button:translate-x-1"
						aria-hidden="true"
					/>
				</Button>
				<Button href="/#works" variant="outline">{HERO.secondaryCta}</Button>
			</div>
		</div>
	</div>
</Section>
