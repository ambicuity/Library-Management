"""Enhanced search functionality with autocomplete and fuzzy matching."""

from typing import List, Dict, Tuple, Set
import re
from collections import defaultdict

try:
    from fuzzywuzzy import fuzz, process

    HAS_FUZZYWUZZY = True
except ImportError:
    HAS_FUZZYWUZZY = False

from .models import Book, Member


class SearchIndex:
    """Search index for fast book and member lookups."""

    def __init__(self) -> None:
        """Initialize the search index."""
        self.title_index: Dict[str, List[Book]] = defaultdict(list)
        self.author_index: Dict[str, List[Book]] = defaultdict(list)
        self.category_index: Dict[str, List[Book]] = defaultdict(list)
        self.member_index: Dict[str, Member] = {}

        # Word-based indexes for autocomplete
        self.title_words: Set[str] = set()
        self.author_words: Set[str] = set()
        self.categories: Set[str] = set()

        # Trigram indexes for fuzzy search fallback
        self.title_trigrams: Dict[str, List[str]] = defaultdict(list)
        self.author_trigrams: Dict[str, List[str]] = defaultdict(list)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words.

        Args:
            text: Text to tokenize

        Returns:
            List of lowercase words
        """
        # Remove punctuation and split into words
        words = re.findall(r"\b\w+\b", text.lower())
        return words

    def _generate_trigrams(self, text: str) -> List[str]:
        """Generate trigrams from text for fuzzy matching.

        Args:
            text: Text to generate trigrams from

        Returns:
            List of trigrams
        """
        text = text.lower().strip()
        if len(text) < 3:
            return [text]

        trigrams = []
        for i in range(len(text) - 2):
            trigrams.append(text[i : i + 3])
        return trigrams

    def add_book(self, book: Book) -> None:
        """Add a book to the search index.

        Args:
            book: Book to add to the index
        """
        # Title indexing
        title_lower = book.title.lower()
        title_words = self._tokenize(book.title)

        for word in title_words:
            self.title_index[word].append(book)
            self.title_words.add(word)

        # Full title indexing
        self.title_index[title_lower].append(book)

        # Author indexing
        author_lower = book.author.lower()
        author_words = self._tokenize(book.author)

        for word in author_words:
            self.author_index[word].append(book)
            self.author_words.add(word)

        # Full author indexing
        self.author_index[author_lower].append(book)

        # Category indexing
        category_lower = book.category.lower()
        self.category_index[category_lower].append(book)
        self.categories.add(book.category)

        # Trigram indexing for fuzzy search
        title_trigrams = self._generate_trigrams(book.title)
        for trigram in title_trigrams:
            self.title_trigrams[trigram].append(book.title)

        author_trigrams = self._generate_trigrams(book.author)
        for trigram in author_trigrams:
            self.author_trigrams[trigram].append(book.author)

    def add_member(self, member: Member) -> None:
        """Add a member to the search index.

        Args:
            member: Member to add to the index
        """
        self.member_index[member.name.lower()] = member

    def clear(self) -> None:
        """Clear all indexes."""
        self.title_index.clear()
        self.author_index.clear()
        self.category_index.clear()
        self.member_index.clear()
        self.title_words.clear()
        self.author_words.clear()
        self.categories.clear()
        self.title_trigrams.clear()
        self.author_trigrams.clear()

    def rebuild(self, books: List[Book], members: List[Member]) -> None:
        """Rebuild the entire search index.

        Args:
            books: List of books to index
            members: List of members to index
        """
        self.clear()

        for book in books:
            self.add_book(book)

        for member in members:
            self.add_member(member)


class EnhancedSearch:
    """Enhanced search functionality with autocomplete and fuzzy matching."""

    def __init__(self) -> None:
        """Initialize the enhanced search system."""
        self.index = SearchIndex()
        self.fuzzy_threshold = 80  # Minimum fuzzy match score

    def update_index(self, books: List[Book], members: List[Member]) -> None:
        """Update the search index with current data.

        Args:
            books: Current list of books
            members: Current list of members
        """
        self.index.rebuild(books, members)

    def get_autocomplete_suggestions(
        self, query: str, search_type: str = "title", limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions for a query.

        Args:
            query: Search query
            search_type: Type of search ("title", "author", "category")
            limit: Maximum number of suggestions

        Returns:
            List of autocomplete suggestions
        """
        query_lower = query.lower()
        suggestions = []

        if search_type == "title":
            # Word-based suggestions
            for word in self.index.title_words:
                if word.startswith(query_lower):
                    suggestions.append(word)

            # Title-based suggestions
            for title in self.index.title_index.keys():
                if title.startswith(query_lower) and title not in suggestions:
                    suggestions.append(title)

        elif search_type == "author":
            # Word-based suggestions
            for word in self.index.author_words:
                if word.startswith(query_lower):
                    suggestions.append(word)

            # Author-based suggestions
            for author in self.index.author_index.keys():
                if author.startswith(query_lower) and author not in suggestions:
                    suggestions.append(author)

        elif search_type == "category":
            # Category suggestions
            for category in self.index.categories:
                if category.lower().startswith(query_lower):
                    suggestions.append(category)

        # Sort by length (shorter suggestions first) and limit
        suggestions.sort(key=len)
        return suggestions[:limit]

    def fuzzy_search_titles(self, query: str, limit: int = 10) -> List[Tuple[str, int]]:
        """Perform fuzzy search on book titles.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (title, score) tuples
        """
        if not HAS_FUZZYWUZZY:
            # Fallback to simple matching
            return self._simple_fuzzy_search_titles(query, limit)

        # Get all unique titles
        titles = set()
        for book_list in self.index.title_index.values():
            for book in book_list:
                titles.add(book.title)

        # Use fuzzy matching
        matches = process.extract(query, titles, scorer=fuzz.partial_ratio, limit=limit)
        return [
            (match[0], match[1])
            for match in matches
            if match[1] >= self.fuzzy_threshold
        ]

    def fuzzy_search_authors(
        self, query: str, limit: int = 10
    ) -> List[Tuple[str, int]]:
        """Perform fuzzy search on book authors.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (author, score) tuples
        """
        if not HAS_FUZZYWUZZY:
            # Fallback to simple matching
            return self._simple_fuzzy_search_authors(query, limit)

        # Get all unique authors
        authors = set()
        for book_list in self.index.author_index.values():
            for book in book_list:
                authors.add(book.author)

        # Use fuzzy matching
        matches = process.extract(
            query, authors, scorer=fuzz.partial_ratio, limit=limit
        )
        return [
            (match[0], match[1])
            for match in matches
            if match[1] >= self.fuzzy_threshold
        ]

    def _simple_fuzzy_search_titles(
        self, query: str, limit: int
    ) -> List[Tuple[str, int]]:
        """Simple fuzzy search fallback for titles using trigrams.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (title, score) tuples
        """
        query_trigrams = set(self.index._generate_trigrams(query))
        title_scores: Dict[str, int] = defaultdict(int)

        for trigram in query_trigrams:
            for title in self.index.title_trigrams.get(trigram, []):
                title_scores[title] += 1

        # Calculate similarity scores
        results = []
        for title, score in title_scores.items():
            title_trigrams = set(self.index._generate_trigrams(title))
            max_trigrams = max(len(query_trigrams), len(title_trigrams))
            if max_trigrams > 0:
                similarity = (score * 100) // max_trigrams
                if similarity >= (
                    self.fuzzy_threshold - 20
                ):  # Lower threshold for fallback
                    results.append((title, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _simple_fuzzy_search_authors(
        self, query: str, limit: int
    ) -> List[Tuple[str, int]]:
        """Simple fuzzy search fallback for authors using trigrams.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (author, score) tuples
        """
        query_trigrams = set(self.index._generate_trigrams(query))
        author_scores: Dict[str, int] = defaultdict(int)

        for trigram in query_trigrams:
            for author in self.index.author_trigrams.get(trigram, []):
                author_scores[author] += 1

        # Calculate similarity scores
        results = []
        for author, score in author_scores.items():
            author_trigrams = set(self.index._generate_trigrams(author))
            max_trigrams = max(len(query_trigrams), len(author_trigrams))
            if max_trigrams > 0:
                similarity = (score * 100) // max_trigrams
                if similarity >= (
                    self.fuzzy_threshold - 20
                ):  # Lower threshold for fallback
                    results.append((author, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def search_books_by_title(self, query: str, fuzzy: bool = False) -> List[Book]:
        """Search books by title with optional fuzzy matching.

        Args:
            query: Search query
            fuzzy: Whether to use fuzzy matching

        Returns:
            List of matching books
        """
        query_lower = query.lower()
        results = []

        if fuzzy:
            # Use fuzzy search
            fuzzy_matches = self.fuzzy_search_titles(query)
            for title, score in fuzzy_matches:
                # Find books with this title
                title_lower = title.lower()
                if title_lower in self.index.title_index:
                    results.extend(self.index.title_index[title_lower])
        else:
            # Exact and partial matching
            for key, books in self.index.title_index.items():
                if query_lower in key:
                    results.extend(books)

        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for book in results:
            book_key = (book.title, book.author)
            if book_key not in seen:
                seen.add(book_key)
                unique_results.append(book)

        return unique_results

    def search_books_by_author(self, query: str, fuzzy: bool = False) -> List[Book]:
        """Search books by author with optional fuzzy matching.

        Args:
            query: Search query
            fuzzy: Whether to use fuzzy matching

        Returns:
            List of matching books
        """
        query_lower = query.lower()
        results = []

        if fuzzy:
            # Use fuzzy search
            fuzzy_matches = self.fuzzy_search_authors(query)
            for author, score in fuzzy_matches:
                # Find books by this author
                author_lower = author.lower()
                if author_lower in self.index.author_index:
                    results.extend(self.index.author_index[author_lower])
        else:
            # Exact and partial matching
            for key, books in self.index.author_index.items():
                if query_lower in key:
                    results.extend(books)

        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for book in results:
            book_key = (book.title, book.author)
            if book_key not in seen:
                seen.add(book_key)
                unique_results.append(book)

        return unique_results

    def search_books_by_category(self, category: str) -> List[Book]:
        """Search books by category.

        Args:
            category: Category to search for

        Returns:
            List of books in the category
        """
        category_lower = category.lower()
        return self.index.category_index.get(category_lower, [])

    def search_members(self, query: str, fuzzy: bool = False) -> List[Member]:
        """Search members by name.

        Args:
            query: Search query
            fuzzy: Whether to use fuzzy matching

        Returns:
            List of matching members
        """
        query_lower = query.lower()
        results = []

        if fuzzy and HAS_FUZZYWUZZY:
            # Use fuzzy search
            member_names = list(self.index.member_index.keys())
            matches = process.extract(
                query, member_names, scorer=fuzz.partial_ratio, limit=10
            )

            for name, score in matches:
                if score >= self.fuzzy_threshold:
                    results.append(self.index.member_index[name])
        else:
            # Exact and partial matching
            for name, member in self.index.member_index.items():
                if query_lower in name:
                    results.append(member)

        return results

    def get_search_statistics(self) -> Dict[str, int]:
        """Get search index statistics.

        Returns:
            Dictionary with index statistics
        """
        return {
            "total_title_entries": len(self.index.title_index),
            "total_author_entries": len(self.index.author_index),
            "total_categories": len(self.index.categories),
            "total_members": len(self.index.member_index),
            "title_words": len(self.index.title_words),
            "author_words": len(self.index.author_words),
            "fuzzy_search_available": HAS_FUZZYWUZZY,
        }


class SearchSuggestionEngine:
    """Engine for providing intelligent search suggestions."""

    def __init__(self, enhanced_search: EnhancedSearch):
        """Initialize the suggestion engine.

        Args:
            enhanced_search: EnhancedSearch instance to use
        """
        self.search = enhanced_search
        self.query_history: List[str] = []
        self.popular_queries: Dict[str, int] = defaultdict(int)

    def record_query(self, query: str) -> None:
        """Record a search query for suggestion improvement.

        Args:
            query: Search query to record
        """
        self.query_history.append(query.lower())
        self.popular_queries[query.lower()] += 1

        # Keep only recent queries
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-500:]

    def get_suggestions(
        self, query: str, search_type: str = "title", limit: int = 10
    ) -> Dict[str, List[str]]:
        """Get comprehensive search suggestions.

        Args:
            query: Search query
            search_type: Type of search
            limit: Maximum number of suggestions per type

        Returns:
            Dictionary with different types of suggestions
        """
        suggestions: Dict[str, List[str]] = {
            "autocomplete": [],
            "fuzzy_matches": [],
            "popular_queries": [],
            "categories": [],
        }

        # Autocomplete suggestions
        suggestions["autocomplete"] = self.search.get_autocomplete_suggestions(
            query, search_type, limit
        )

        # Fuzzy match suggestions
        if search_type == "title":
            fuzzy_matches = self.search.fuzzy_search_titles(query, limit)
            suggestions["fuzzy_matches"] = [match[0] for match in fuzzy_matches]
        elif search_type == "author":
            fuzzy_matches = self.search.fuzzy_search_authors(query, limit)
            suggestions["fuzzy_matches"] = [match[0] for match in fuzzy_matches]

        # Popular query suggestions
        query_lower = query.lower()
        popular = [
            q
            for q, count in sorted(
                self.popular_queries.items(), key=lambda x: x[1], reverse=True
            )
            if query_lower in q and q != query_lower
        ]
        suggestions["popular_queries"] = popular[:limit]

        # Category suggestions
        if search_type == "category" or search_type == "title":
            suggestions["categories"] = self.search.get_autocomplete_suggestions(
                query, "category", limit
            )

        return suggestions
