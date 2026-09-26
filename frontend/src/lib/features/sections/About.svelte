<script lang="ts">
	import Check from '@lucide/svelte/icons/check';
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { ABOUT } from '$lib/content/home';
	import type { ImageAsset } from '$lib/types';
	import { reveal } from '$lib/utils';

	interface Props {
		image: ImageAsset | null;
	}

	let { image }: Props = $props();
</script>

<Section id="about">
	<div class="grid items-center gap-12 lg:grid-cols-2 lg:gap-20">
		<div use:reveal>
			<p class="mb-5 text-xs font-medium tracking-widest text-muted-foreground uppercase">
				{ABOUT.eyebrow}
			</p>
			<h2
				class="text-4xl leading-[1.08] font-light text-balance text-primary sm:text-5xl lg:text-[3.5rem]"
			>
				{ABOUT.title}
			</h2>
			<p class="mt-7 max-w-xl text-lg leading-relaxed text-muted-foreground">{ABOUT.text}</p>
			<ul class="mt-9 grid gap-x-6 gap-y-4 sm:grid-cols-2">
				{#each ABOUT.points as point (point)}
					<li class="flex items-start gap-3">
						<span
							class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/10"
							aria-hidden="true"
						>
							<Check class="size-3 text-primary" strokeWidth={2.5} />
						</span>
						<span class="text-foreground/85">{point}</span>
					</li>
				{/each}
			</ul>
		</div>
		<div class="relative" use:reveal={80}>
			<div class="aspect-[4/5] lift-hover overflow-hidden rounded-[2rem]">
				<ResponsiveImage
					{image}
					sizes="(min-width: 1024px) 50vw, 100vw"
					class="size-full object-cover"
				/>
			</div>
			<div
				class="absolute -top-5 -right-3 max-w-[14rem] rounded-2xl px-5 py-4 shadow-float glass sm:-right-6"
			>
				<p class="font-display text-2xl text-primary">{ABOUT.badgeTitle}</p>
				<p class="text-sm text-muted-foreground">{ABOUT.badgeText}</p>
			</div>
		</div>
	</div>
</Section>
