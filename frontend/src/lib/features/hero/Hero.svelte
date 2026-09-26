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

<Section id="hero" class="relative flex min-h-[100svh] items-center pt-28 pb-16 md:pt-32 md:pb-16">
	<div class="grid items-center gap-10 lg:grid-cols-12 lg:gap-12">
		<div class="z-10 lg:col-span-6">
			<h1
				class="text-[2.75rem] leading-[1.05] font-light text-balance text-primary sm:text-6xl lg:text-[5rem]"
			>
				{HERO.title}
			</h1>
			<p class="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">{HERO.subtitle}</p>
			<div class="mt-9 flex flex-col gap-3 sm:flex-row">
				<Button href="/lead" onclick={(event: MouseEvent) => openFromLink(event)}>
					{HERO.cta}
					<ArrowRight
						class="transition-transform group-hover/button:translate-x-1"
						aria-hidden="true"
					/>
				</Button>
				<Button href="/#works" variant="secondary">{HERO.secondaryCta}</Button>
			</div>
		</div>
		<div class="relative lg:col-span-6">
			<div
				class="relative aspect-[4/5] overflow-hidden rounded-[2rem] sm:aspect-[5/4] lg:aspect-[4/5]"
			>
				<!-- The LCP element: eager and high priority (tech.md, S1-09). -->
				<ResponsiveImage
					{image}
					sizes="100vw"
					loading="eager"
					fetchpriority="high"
					class="size-full object-cover"
				/>
				<div
					class="absolute inset-0 bg-linear-to-t from-primary/25 via-transparent to-transparent"
				></div>
			</div>
			<div
				class="absolute -bottom-5 -left-3 max-w-[15rem] rounded-2xl px-5 py-4 shadow-float glass sm:-left-6"
			>
				<p class="text-xs font-medium tracking-wider text-muted-foreground uppercase">
					{HERO.badgeLabel}
				</p>
				<p class="mt-1 font-display text-lg text-primary">{HERO.badgeValue}</p>
			</div>
		</div>
	</div>
</Section>
