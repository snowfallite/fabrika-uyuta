<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { ADVANTAGES } from '$lib/content/home';
	import { reveal } from '$lib/utils';

	const number = (index: number) => String(index + 1).padStart(2, '0');
</script>

<Section id="advantages" title={ADVANTAGES.title} subtitle={ADVANTAGES.eyebrow} tone="muted">
	<ul class="grid gap-5 sm:grid-cols-2 md:gap-7 lg:grid-cols-4">
		{#each ADVANTAGES.items as item, index (item.title)}
			<li class="lift-hover rounded-[1.5rem] p-7 glass" use:reveal={index * 70}>
				<span
					aria-hidden="true"
					data-n={number(index)}
					class="font-display text-4xl font-light text-primary/25 before:content-[attr(data-n)]"
				></span>
				<h3 class="mt-4 text-2xl text-primary">{item.title}</h3>
				<p class="mt-3 leading-relaxed text-muted-foreground">{item.text}</p>
			</li>
		{/each}
	</ul>
</Section>
