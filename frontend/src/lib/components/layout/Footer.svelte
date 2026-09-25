<script lang="ts">
	import type { NavItem } from '$lib/config/nav';
	import { BRAND, FOOTER, LEAD_CTA } from '$lib/content/layout';
	import type { SiteSettings } from '$lib/types';

	interface Props {
		settings: SiteSettings;
		nav: NavItem[];
	}

	let { settings, nav }: Props = $props();
	const year = new Date().getFullYear();
</script>

<footer class="bg-primary text-primary-foreground">
	<div class="mx-auto max-w-7xl px-5 py-16 md:px-8 md:py-20">
		<div class="grid gap-10 md:grid-cols-12">
			<div class="md:col-span-5">
				<p class="font-display text-3xl">{BRAND}</p>
				<p class="mt-4 max-w-sm leading-relaxed text-primary-foreground/80">{FOOTER.about}</p>
				<ul class="mt-6 space-y-1.5 text-sm text-primary-foreground/80">
					{#if settings.address}
						<li>{settings.address}</li>
					{/if}
					{#if settings.phone}
						<li>
							<a href="tel:{settings.phone}" class="hover:text-primary-foreground"
								>{settings.phone_display}</a
							>
						</li>
					{/if}
					{#if settings.email}
						<li>
							<a href="mailto:{settings.email}" class="hover:text-primary-foreground"
								>{settings.email}</a
							>
						</li>
					{/if}
				</ul>
			</div>
			<nav aria-labelledby="footer-nav-title" class="md:col-span-3">
				<p
					id="footer-nav-title"
					class="mb-4 text-xs font-medium tracking-widest text-primary-foreground/80 uppercase"
				>
					{FOOTER.navTitle}
				</p>
				<ul class="space-y-2.5">
					{#each nav as item (item.href)}
						<li>
							<a
								href={item.href}
								class="text-primary-foreground/80 transition-colors hover:text-primary-foreground"
								>{item.label}</a
							>
						</li>
					{/each}
				</ul>
			</nav>
			<div class="md:col-span-4">
				<p class="mb-4 text-xs font-medium tracking-widest text-primary-foreground/80 uppercase">
					{FOOTER.leadTitle}
				</p>
				<p class="mb-5 text-primary-foreground/80">{FOOTER.leadText}</p>
				<a
					href="/lead"
					class="inline-flex items-center rounded-full bg-primary-foreground/10 px-5 py-2.5 text-sm font-medium transition-colors hover:bg-primary-foreground/20"
					>{LEAD_CTA}</a
				>
			</div>
		</div>
		<div
			class="mt-14 flex flex-col items-center justify-between gap-3 border-t border-primary-foreground/15 pt-6 text-sm text-primary-foreground/80 sm:flex-row"
		>
			<p>© {year} {FOOTER.rights}</p>
			<div class="flex flex-col items-center gap-2 sm:flex-row sm:gap-6">
				<a href="/privacy" class="hover:text-primary-foreground">{FOOTER.privacy}</a>
				<a href="/consent" class="hover:text-primary-foreground">{FOOTER.consent}</a>
			</div>
		</div>
	</div>
</footer>
