import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        concepts: z.array(z.string()).optional(),
        difficulty: z.string().optional(),
        projectId: z.string().optional(),
        time: z.string().optional(),
        concept: z.string().optional(),
        usedIn: z.array(z.string()).optional(),
        order: z.number().optional(),
        arc: z.enum(['part-1', 'part-2']).optional(),
        caseNumber: z.string().optional(),
        format: z.string().optional(),
        datasetIds: z.array(z.string()).optional(),
        notebook: z.string().optional(),
        solutionNotebook: z.string().optional(),
        archive: z.string().optional(),
        prerequisite: z.string().optional(),
      }),
    }),
  }),
};
