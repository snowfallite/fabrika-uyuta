<script lang="ts">
	import Menu from '@lucide/svelte/icons/menu';
	import Phone from '@lucide/svelte/icons/phone';
	import * as Sheet from '$lib/components/ui/sheet';
	import { buttonVariants } from '$lib/components/ui/button';
	import type { NavItem } from '$lib/config/nav';
	import { LEAD_CTA, MENU_TITLE } from '$lib/content/layout';
	import { formatPhoneInput } from '$lib/domain/phone';

	interface Props {
		nav: NavItem[];
		/** E.164 or empty. */
		phone: string;
	}

	let { nav, phone }: Props = $props();
	let open = $state(false);
</script>

<Sheet.Root bind:open>
	<Sheet.Trigger
		class="{buttonVariants({ variant: 'secondary', size: 'icon' })} lg:hidden"
		aria-label={MENU_TITLE}
	>
		<Menu class="size-5" aria-hidden="true" />
	</Sheet.Trigger>
	<Sheet.Content side="right" class="w-[85%] p-6 pt-16">
		<Sheet.Title class="sr-only">{MENU_TITLE}</Sheet.Title>
		<nav aria-label={MENU_TITLE} class="flex flex-col gap-1">
			{#each nav as item (item.href)}
				<a
					href={item.href}
					class="rounded-xl px-3 py-3 text-base font-medium text-foreground/80 transition-colors hover:bg-secondary/60"
					onclick={() => (open = false)}>{item.label}</a
				>
			{/each}
		</nav>
		<div class="mt-4 flex flex-col gap-3 border-t border-border pt-6">
			{#if phone}
				<a href="tel:{phone}" class="flex items-center gap-2 px-3 font-medium text-primary">
					<Phone class="size-4" aria-hidden="true" />{formatPhoneInput(phone)}
				</a>
			{/if}
			<a href="/lead" class={buttonVariants({ size: 'sm' })} onclick={() => (open = false)}
				>{LEAD_CTA}</a
			>
		</div>
	</Sheet.Content>
</Sheet.Root>
