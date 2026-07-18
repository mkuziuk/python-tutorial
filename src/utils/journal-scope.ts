/**
 * Route-derived edition scope for the «Полевой журнал» design system.
 *
 * The visual arc (Part I archive vs. Part II bureau) and the page variant
 * (overview / lesson / solution) are computed from the Starlight route id
 * alone, so Markdown files never need per-page markup to be themed.
 */

export type JournalArc = 'part-1' | 'part-2';
export type JournalVariant = 'overview' | 'lesson' | 'solution';

export interface JournalScope {
	arc: JournalArc;
	variant: JournalVariant;
}

/**
 * Returns the journal scope for a Starlight route id (e.g. `cases/phishing-email`),
 * or `null` for pages outside the two arcs (field guide, materials, 404, …).
 */
export function getJournalScope(routeId: string): JournalScope | null {
	// `index.md` routes keep their directory as id, but normalize defensively.
	const slug = routeId.replace(/\/index$/, '');

	if (slug === 'cases') return { arc: 'part-1', variant: 'overview' };
	if (slug === 'bureau') return { arc: 'part-2', variant: 'overview' };

	if (slug.startsWith('cases/')) {
		return { arc: 'part-1', variant: slug.endsWith('-solution') ? 'solution' : 'lesson' };
	}
	if (slug.startsWith('bureau/')) {
		return { arc: 'part-2', variant: slug.endsWith('-solution') ? 'solution' : 'lesson' };
	}
	return null;
}
