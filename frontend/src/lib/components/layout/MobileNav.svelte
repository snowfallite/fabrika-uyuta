<script lang="ts">
	import Menu from '@lucide/svelte/icons/menu';
	import Phone from '@lucide/svelte/icons/phone';
	import * as Sheet from '$lib/components/ui/sheet';
	import { buttonVariants } from '$lib/components/ui/button';
	import type { NavItem } from '$lib/config/nav';
	import { LEAD_CTA, MENU_TITLE } from '$lib/content/layout';
	import { formatPhoneInput } from '$lib/domain/phone';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import { cn } from '$lib/utils';

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
		class={cn(buttonVariants({ variant: 'secondary', size: 'icon' }), 'lg:hidden')}
		aria-label={MENU_TITLE}
	>
		<Menu class="size-5" aria-hidden="true" />
	</Sheet.Trigger>
	<!-- Scrolls on its own: in landscape the menu is taller than the screen. -->
	<Sheet.Content side="right" class="w-[85%] overflow-y-auto overscroll-contain p-6 pt-5">
		<Sheet.Title class="flex h-11 items-center pr-12">{MENU_TITLE}</Sheet.Title>
		<nav aria-label={MENU_TITLE} class="flex flex-col gap-1">
			{#each nav as item (item.href)}
				<a
					href={item.href}
					class="rounded-xl px-3 py-3 text-base font-medium text-foreground/80 transition-colors hover:bg-secondary/60"
					onclick={() => (open = false)}>{item.label}</a
				>
			{/each}
		</nav>
		<div class="mt-2 flex flex-col gap-3 border-t border-border pt-5">
			{#if phone}
				<a href="tel:{phone}" class="flex items-center gap-2 px-3 py-2 font-medium text-primary">
					<Phone class="size-4" aria-hidden="true" />{formatPhoneInput(phone)}
				</a>
			{/if}
			<a
				href="/lead"
				class={buttonVariants({ size: 'sm' })}
				onclick={(event) => {
					open = false;
					openFromLink(event);
				}}>{LEAD_CTA}</a
			>
		</div>
	</Sheet.Content>
</Sheet.Root>
