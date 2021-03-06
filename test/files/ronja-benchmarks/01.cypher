match (toFrom:Entity{Id:{eId}}), segment-[:precedes|is]->startSegment, toFrom-[toFrom_rel:read|wrote]->startSegment with segment match segment-[:regarding_summary_phrase]->entity with segment, entity match checkIgnoredWriter-[:wrote]->segment where ((checkIgnoredWriter.Rank > 0 or checkIgnoredWriter.Rank is null)) and ((entity.Rank > 0 or entity.Rank is null)) and (NOT(entity.Id = {eId})) RETURN entity.Id as Id, entity.Name as Name, entity.Type as Type, entity.MentionNames as Mentions, count(distinct segment) as SegmentCount order by SegmentCount desc skip 0 limit 51