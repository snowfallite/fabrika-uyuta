<script lang="ts">
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import { BREADCRUMBS } from '$lib/content/layout';
	import type { Crumb } from '$lib/domain/json-ld';

	interface Props {
		items: Crumb[];
		class?: string;
	}

	let { items, class: className = '' }: Props = $props();
</script>

<nav aria-label={BREADCRUMBS} class={className}>
	<ol class="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
		{#each items as item, index (item.label)}
			<li class="flex items-center gap-x-2">
				{#if index > 0}
					<ChevronRight class="size-3.5 shrink-0 opacity-70" aria-hidden="true" />
				{/if}
				{#if item.href}
					<a href={item.href} class="transition-colors hover:text-primary">{item.label}</a>
				{:else}
					<span aria-current="page" class="text-foreground">{item.label}</span>
				{/if}
			</li>
		{/each}
	</ol>
</nav>
