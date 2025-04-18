# Issue 8: Cooking Notes section incorrectly includes user comments

## Issue Description

The Cooking Notes section in plant data includes user comments and questions that are not related to cooking instructions. For example, in the Beets entry, the Cooking Notes section contains user questions about Japanese beetles, growing conditions, and other unrelated topics.

## Expected Behavior

The Cooking Notes section should only contain information related to cooking and preparing the plant, not user comments or questions.

## Current Behavior

Currently, the Cooking Notes section includes user comments and questions that are unrelated to cooking. For example, in the Beets entry, there are comments about:
- Questions about why beets aren't forming round roots
- Methods for growing beets
- Questions about Japanese beetles on grape vines
- Stories about using ducks to control Japanese beetles

## Example from Beets Entry

```
"Cooking Notes": "Beets are a nutrient-dense food considered especially beneficial for health. Learn more in â€œ
Beets: Health Benefits !â€\nWhy are my beets not forming a round balled root?\nHi Larry. Unfortunately there is no
simple answer. Your beets are putting more energy into leaf production than root production. This could be due to many
factors such as too much nitrogen in the soil or overall poor soil quality not getting enough sunlight inconsistent
watering the plants may be too crowded or if you planted by seed they may have been planted too deep.\n1 tablespoon
3% hydrogen peroxide and 1 cup of water for 24 hours. Place a paper towel in a container fold it over pour mixture over
paper towel until damp unfold the towel and spread seeds. fold towel again and add enough solution to keep damp over
night.\nSo where can you grow them anywhere?\nChoose a planting site that gets full sun. Beets should ideally receive at
least 6 hours of direct sunlight per day. Beets grow best in well-prepared fertile soil but will tolerate average to
low soil fertility.\nIn the summer I am suddenly bombarded with Japanese Beetles on my beautiful grape vines what will
get rid of them and not harm my pets?\nJapanese beetles are mature grubs that are in your soil. Use milky spore on your
grass and soil (itâ€™s organic). Spring is a great time to apply. It will kill the grubs and eliminate the Japanese
beetles. There are some milky spore brands that only require one application\nJapanese beetles fly long distances from
where they hatched in grassy areas. All they care about is mating & eating. Treating your yard for them will not stop the
ones flying in from golf courses & other folks' yards. They love Linden trees birch & crab apple trees grapes rose
blossoms & respberries among others. Brush them off into a cottage cheese container that has water a couple drops of
dish soap & a quick spray of flying insect spray. Some fly back out but once they've been in the insect spray & soap
they will die quickly. Dispose of them in your garden compost bin or flower beds. I sometimes spray large clusters of
them with flying insect killer. Don't ever use the beetle traps. They draw in thousands of beetles from far away. I did
that once & gathered 5 gallons of them daily from the 3 traps I set out. A full time job!\nJapanese beetles fly long
distances from where they hatched in grassy areas. All they care about is mating & eating. Treating your yard for them
will not stop the ones flying in from golf courses & other folks' yards. They love Linden trees birch & crab apple
trees grapes rose blossoms & respberries among others. Brush them off into a cottage cheese container that has waster
a couple drops of dish soap & a quick spray of flying insect spray\nWee had a pet duck. He loved them. We hold him and
aim him at the beetles and they were gone. He would eat 150 or more a day. In a few days they were hard to find."
```

## Proposed Solution

Filter out user comments from the Cooking Notes section during the scraping or transformation process. This could be done by:
1. Identifying patterns that indicate user comments (e.g., question format, usernames)
2. Only including content that appears to be official cooking instructions
3. Possibly creating a separate section for user tips if they're valuable

## Affected Files

- `src/notion/transformer.py`
- `scripts/sync_to_notion_requests.py`
- Any scraper files that extract the Cooking Notes content

## GitHub Issue Link

[Issue #8: Cooking Notes section incorrectly includes user comments](https://github.com/niklas-joh/plantScraper/issues/8)

## Status

- Created: April 18, 2025
- Status: Open
- Labels: bug
