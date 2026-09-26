<script lang="ts">
	import Phone from '@lucide/svelte/icons/phone';
	import { buttonVariants } from '$lib/components/ui/button';
	import type { NavItem } from '$lib/config/nav';
	import { BRAND, CALL_LABEL, LEAD_CTA } from '$lib/content/layout';
	import type { SiteSettings } from '$lib/types';
	import { cn } from '$lib/utils';
	import { openFromLink } from '$lib/features/lead-form/dialog.svelte';
	import MobileNav from './MobileNav.svelte';

	interface Props {
		settings: SiteSettings;
		nav: NavItem[];
	}

	let { settings, nav }: Props = $props();

	let scrollY = $state(0);
	// Glass pill after 24px of scroll, as in the template header.
	const scrolled = $derived(scrollY > 24);
</script>

<svelte:window bind:scrollY />

<header
	class={cn('fixed inset-x-0 top-0 z-50 transition-all duration-500', scrolled ? 'py-3' : 'py-4')}
>
	<div class="mx-auto max-w-7xl px-5 md:px-8">
		<!-- At the top the row lines up with the page content; the pill padding appears on scroll. -->
		<div
			class={cn(
				'flex items-center justify-between gap-4 rounded-full py-2 transition-all duration-500',
				scrolled ? 'px-4 shadow-header glass md:px-6' : 'bg-transparent px-0'
			)}
		>
			<a
				href="/"
				class="font-display text-[1.75rem] leading-none font-medium tracking-tight whitespace-nowrap text-primary md:text-[2rem]"
			>
				{BRAND}
			</a>
			<nav aria-label="Основное меню" class="hidden items-center gap-4 lg:flex xl:gap-6">
				{#each nav as item (item.href)}
					<a
						href={item.href}
						class="text-sm font-medium whitespace-nowrap text-foreground/75 transition-colors hover:text-primary"
						>{item.label}</a
					>
				{/each}
			</nav>
			<div class="flex items-center gap-2 sm:gap-3">
				{#if settings.phone}
					<a
						href="tel:{settings.phone}"
						class="hidden items-center gap-2 text-sm font-medium whitespace-nowrap text-primary xl:inline-flex"
					>
						<Phone class="size-4" aria-hidden="true" />{settings.phone_display}
					</a>
					<a
						href="tel:{settings.phone}"
						aria-label="{CALL_LABEL} {settings.phone_display}"
						class={cn(buttonVariants({ variant: 'secondary', size: 'icon' }), 'lg:hidden')}
					>
						<Phone class="size-5" aria-hidden="true" />
					</a>
				{/if}
				<a
					href="/lead"
					class={cn(buttonVariants({ size: 'sm' }), 'hidden sm:inline-flex')}
					onclick={(event) => openFromLink(event)}>{LEAD_CTA}</a
				>
				<MobileNav {nav} phone={settings.phone} />
			</div>
		</div>
	</div>
</header>
