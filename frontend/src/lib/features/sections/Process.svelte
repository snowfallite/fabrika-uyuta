<script lang="ts">
	import { Section } from '$lib/components/ui/section';
	import { PROCESS } from '$lib/content/home';
	import { reveal } from '$lib/utils';

	const number = (index: number) => String(index + 1).padStart(2, '0');
</script>

<Section id="process" title={PROCESS.title} subtitle={PROCESS.eyebrow}>
	<div class="relative">
		<div
			class="absolute inset-x-0 top-12 hidden h-px joinery-line md:block"
			aria-hidden="true"
		></div>
		<ol class="relative grid gap-px md:grid-cols-5">
			{#each PROCESS.steps as step, index (step.title)}
				<li class="relative bg-background px-1 py-6 md:py-0" use:reveal={index * 80}>
					<div class="flex items-center gap-4 md:block">
						<!-- Pale step number as generated content: decoration outside contrast checks. -->
						<span
							aria-hidden="true"
							data-n={number(index)}
							class="font-display text-5xl font-light text-primary/25 before:content-[attr(data-n)]"
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
