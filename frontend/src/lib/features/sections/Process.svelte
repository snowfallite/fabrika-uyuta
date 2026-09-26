<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { PROCESS } from '$lib/content/home';
	import { reveal } from '$lib/utils';

	const number = (index: number) => String(index + 1).padStart(2, '0');
</script>

<Section id="process" title={PROCESS.title} subtitle={PROCESS.eyebrow}>
	<div class="relative">
		<div
			class="absolute inset-x-0 top-6 hidden h-px joinery-line md:block"
			aria-hidden="true"
		></div>
		<ol class="relative grid md:grid-cols-5 md:gap-6">
			{#each PROCESS.steps as step, index (step.title)}
				<li class="relative px-1 py-4 md:py-0" use:reveal={index * 80}>
					<div class="flex items-center gap-4 md:block">
						<!-- Pale step number as generated content: decoration outside contrast checks. -->
						<span
							aria-hidden="true"
							data-n={number(index)}
							class="relative inline-block min-w-14 bg-background pr-4 font-display text-5xl font-light text-primary/40 before:content-[attr(data-n)]"
						></span>
						<div class="md:mt-6">
							<h3 class="text-2xl text-primary">{step.title}</h3>
							<p class="mt-2 text-sm leading-relaxed text-muted-foreground">{step.text}</p>
						</div>
					</div>
				</li>
			{/each}
		</ol>
	</div>
</Section>
