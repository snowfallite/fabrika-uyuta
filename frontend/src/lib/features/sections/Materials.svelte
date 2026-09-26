<script lang="ts">
	import { ResponsiveImage } from '$lib/components/ui/responsive-image';
	import { Section } from '$lib/components/ui/section';
	import { MATERIALS } from '$lib/content/home';
	import type { HomeSlots } from '$lib/types';
	import { reveal } from '$lib/utils';

	interface Props {
		slots: HomeSlots;
	}

	let { slots }: Props = $props();
</script>

<Section id="materials" title={MATERIALS.title} subtitle={MATERIALS.eyebrow} tone="muted">
	<div class="grid gap-5 md:grid-cols-2 md:gap-7">
		{#each MATERIALS.items as material, index (material.slot)}
			<article
				class="group grid lift-hover gap-5 rounded-[1.75rem] p-5 glass sm:grid-cols-5"
				use:reveal={index * 80}
			>
				<div class="aspect-[4/3] overflow-hidden rounded-2xl sm:col-span-2">
					<ResponsiveImage
						image={slots[material.slot]}
						sizes="(min-width: 768px) 20vw, 100vw"
						aspect="4/3"
						class="size-full object-cover transition-transform duration-700 group-hover:scale-105"
					/>
				</div>
				<div class="flex flex-col justify-center sm:col-span-3">
					<h3 class="text-3xl text-primary">{material.title}</h3>
					<p class="mt-3 leading-relaxed text-muted-foreground">{material.text}</p>
				</div>
			</article>
		{/each}
	</div>
</Section>
