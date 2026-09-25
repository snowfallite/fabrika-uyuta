export type NavItem = { label: string; href: string };

// The menu changes here, never in markup (tech.md, 10.5).
export const NAV: NavItem[] = [
	{ label: 'О компании', href: '/#about' },
	{ label: 'Направления', href: '/#catalog' },
	{ label: 'Галерея', href: '/#works' },
	{ label: 'Материалы', href: '/#materials' },
	{ label: 'Как мы работаем', href: '/#process' },
	{ label: 'Контакты', href: '/#contacts' }
];
