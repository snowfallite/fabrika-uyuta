<script lang="ts">
	import ArrowUpRight from '@lucide/svelte/icons/arrow-up-right';
	import { Section } from '$lib/components/ui/section';
	import { CATEGORY_PAGE } from '$lib/content/pages';
	import type { ProductOption } from '$lib/types';

	interface Props {
		current: string;
		options: ProductOption[];
	}

	let { current, options }: Props = $props();

	// The published categories already ride along in the settings, so this costs no query.
	const others = $derived(options.filter((option) => option.value !== current));
</script>

{#if others.length > 0}
	<Section id="other-categories" title={CATEGORY_PAGE.otherTitle}>
		<ul class="flex flex-wrap gap-3">
			{#each others as option (option.value)}
				<li>
					<a
						href="/catalog/{option.value}"
						class="inline-flex items-center gap-2 rounded-full border border-border bg-card px-5 py-2.5 text-sm font-medium transition-colors hover:border-primary hover:text-primary"
					>
						{option.label}
						<ArrowUpRight class="size-4 shrink-0" aria-hidden="true" />
					</a>
				</li>
			{/each}
		</ul>
	</Section>
{/if}
