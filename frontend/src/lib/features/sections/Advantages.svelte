<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { ADVANTAGES } from '$lib/content/home';
	import { reveal } from '$lib/utils';

	const number = (index: number) => String(index + 1).padStart(2, '0');
</script>

<Section id="advantages" title={ADVANTAGES.title} subtitle={ADVANTAGES.eyebrow} tone="muted">
	<ul class="grid grid-cols-2 gap-3 sm:gap-5 md:gap-6 lg:grid-cols-4">
		{#each ADVANTAGES.items as item, index (item.title)}
			<li class="rounded-[1.5rem] p-5 glass md:p-7" use:reveal={index * 70}>
				<span
					aria-hidden="true"
					data-n={number(index)}
					class="font-display text-3xl font-light text-primary/40 before:content-[attr(data-n)] md:text-4xl"
				></span>
				<h3 class="mt-3 text-xl text-primary md:mt-4 md:text-2xl">{item.title}</h3>
				<p class="mt-2 text-sm leading-relaxed text-muted-foreground md:mt-3 md:text-base">
					{item.text}
				</p>
			</li>
		{/each}
	</ul>
</Section>
