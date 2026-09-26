package com.gachiguild.gachitoefl.data.local

/**
 * TOEFL学術語彙をレベル（1〜5）に分類するクラス。
 *
 * レベル設計:
 *  - Level 1: Foundation（基礎）: 高頻度の必須語彙
 *  - Level 2: Academic Core（標準）: アカデミックな標準語彙
 *  - Level 3: TOEFL Academic（応用）: 高度なアカデミック語彙
 *  - Level 4: Advanced Academic（発展）: 講義・研究で使う高度語彙
 */
object VocabularyClassifier {
    /** Level 1（基礎）: 高校基礎〜英検2級程度の基本的な語（build_vocabulary.py の LEVEL1_WORDS と一致） */
    private val level1Words = setOf(
        "a", "about", "after", "again", "all", "also", "an", "and", "any", "are",
        "as", "at", "back", "be", "because", "been", "before", "being", "between",
        "both", "but", "by", "came", "can", "come", "could", "day", "did", "do",
        "down", "each", "even", "every", "few", "first", "for", "from", "get", "go",
        "good", "got", "great", "had", "has", "have", "he", "her", "here", "him",
        "his", "how", "i", "if", "in", "into", "is", "it", "its", "just", "know",
        "like", "little", "long", "make", "made", "man", "many", "may", "me",
        "might", "more", "most", "much", "must", "my", "never", "new", "no", "not",
        "now", "of", "off", "old", "on", "one", "only", "or", "other", "our", "out",
        "over", "own", "people", "place", "right", "said", "same", "say", "see",
        "she", "should", "since", "so", "some", "still", "such", "take", "than",
        "that", "the", "their", "them", "then", "there", "these", "they", "thing",
        "this", "those", "three", "through", "time", "to", "two", "under", "up",
        "us", "use", "very", "was", "way", "we", "well", "what", "when", "where",
        "which", "while", "who", "why", "will", "with", "work", "world", "would",
        "year", "you", "your"
    )

    /** Level 2（標準）: アカデミックな標準語彙 */
    private val level2Roots = listOf(
        "analy", "accur", "benefi", "signific", "establish", "demonstrat", "interpret",
        "contribut", "consequent", "furthermore", "nevertheless", "emphasiz", "acquire",
        "assume", "conduct", "evident", "initially", "subsequent", "ultimately", "adapt",
        "alter", "approach", "available", "concept", "derive", "distinct", "element",
        "ensure", "estimate", "evaluation", "exclude", "explicit", "exposure", "external",
        "generate", "identify", "illustrate", "impact", "indicate", "individual",
        "influence", "instance", "issue", "maintain", "majority", "method", "minimal",
        "modify", "monitor", "objective", "obtain", "occur", "option", "outcome",
        "overall", "perceive", "perspective", "potential", "precise", "principle",
        "procedure", "proportion", "pursue", "relevant", "reluctant", "resolve",
        "accommodate", "accompany", "account", "accumulate", "acknowledge", "adequate",
        "adjust", "administer", "advocate", "affect", "allocate", "alternative",
        "anticipate", "apparent", "appeal", "appropriate", "assess", "assign", "assist",
        "attach", "attain", "attribute", "authentic", "aware", "barrier", "capacity",
        "category", "challenge", "character", "circumstance", "cite", "clarify",
        "coherent", "commit", "compatible", "competent", "component", "compromise",
        "confirm", "conform", "consecutive", "consent", "consistent", "constitute",
        "consult", "consume", "contemporary", "convert", "convey", "convince",
        "cooperate", "coordinate", "correspond", "criterion", "crucial", "cultivate",
        "declare", "decline", "decrease", "deduce", "depict", "designate", "devise",
        "diligent", "diminish", "disclose", "distinct", "diverse", "domestic",
        "dominant", "draft", "drastic", "economic", "efficient", "eliminate", "emerge",
        "enable", "enhance", "enormous", "evaluate", "evolve", "expand", "expert",
        "factor", "feasible", "flexible", "fluctuat", "focus", "foundation", "function",
        "fundamental", "grant", "guarantee", "identical", "ignore", "imply", "include",
        "incorporate", "inevitable", "inherent", "initiative", "intense", "interact",
        "justify", "knowledge", "legitimate", "leisure", "liable", "limit", "logic",
        "marginal", "maximize", "notion", "notion", "obligation", "obvious", "occupy",
        "opposite", "originate", "particular", "passive", "percentage", "permanent",
        "permit", "persistent", "phase", "phenomenon", "portion", "positive", "precede",
        "predict", "preliminary", "presume", "prevail", "priority", "proclaim",
        "productive", "profound", "prohibit", "promote", "prompt", "prospect", "prosper",
        "protest", "prove", "provoke", "prudent", "qualify", "quantity", "radical",
        "random", "range", "rational", "react", "realistic", "reasonable", "recover",
        "reflect", "regulate", "reinforce", "reject", "relative", "relax", "release",
        "reliable", "rely", "remove", "render", "replace", "represent", "require",
        "resemble", "reserve", "resist", "resource", "respond", "restore", "restrict",
        "retain", "reveal", "revenue", "reverse", "revise", "reward", "rural",
        "satisfy", "schedule", "secure", "seek", "select", "sensitive", "separate",
        "series", "severe", "shift", "similar", "simulate", "slight", "source",
        "specific", "specify", "stable", "standard", "status", "stimulate", "strategy",
        "structure", "sufficient", "suitable", "supplement", "survive", "symbol",
        "temporary", "tendency", "terminate", "transfer", "transform", "transition",
        "transport", "typical", "undertake", "unify", "unique", "utilize", "valid",
        "vary", "vehicle", "venture", "verify", "viable", "voluntary", "vulnerable",
        "welfare", "widespread"
    )

    /** Level 3（応用）: TOEFLで頻出する高度なアカデミック語彙 */
    private val level3Roots = listOf(
        "ambiguous", "analogous", "arbitrary", "articulate", "coincide", "collapse",
        "compensate", "conceive", "condense", "confer", "configure", "consolidate",
        "constraint", "contradict", "conventional", "cumulative", "deficiency", "deplete",
        "deteriorate", "differentiate", "discriminate", "displace", "dispose", "disrupt",
        "distort", "dwell", "elaborate", "embody", "empirical", "endeavor", "enhance",
        "envisage", "equilibrium", "exacerbate", "exemplify", "exert", "expenditure",
        "explicit", "feasible", "formulate", "hierarchy", "homogeneous", "hypothesis",
        "implement", "implication", "implicit", "incentive", "incorporate", "indigenous",
        "infer", "infrastructure", "inherent", "innovation", "institution", "intellectual",
        "intervene", "intrinsic", "investigate", "legislation", "mechanism", "migration",
        "minimize", "notwithstanding", "obsolete", "paradigm", "parameter", "perpetuate",
        "plausible", "predominant", "presume", "prevalence", "profound", "prohibition",
        "proportion", "qualitative", "quantitative", "rationale", "reciprocal",
        "redundancy", "reinforce", "resilience", "scrutinize", "simultaneous", "skeptical",
        "sophisticated", "spontaneous", "subsequent", "subsidiary", "subsidy",
        "substitute", "supplementary", "suppress", "surpass", "sustainable", "tangible",
        "theoretical", "transaction", "transcend", "transient", "underlying",
        "unprecedented", "validate"
    )

    /** Level 4（発展）: 講義・研究で使う専門性の高い語彙 */
    private val level4Roots = listOf(
        "aberrant", "abstruse", "acquiesce", "admonish", "adroit", "amorphous",
        "anachronism", "anomaly", "antithesis", "apathy", "arbiter", "archaic",
        "assiduous", "autonomy", "banal", "benevolent", "bourgeois", "capricious",
        "catalyst", "circumvent", "cogent", "colloquial", "commensurate", "complacent",
        "concomitant", "conjecture", "connoisseur", "consensus", "conspicuous",
        "contentious", "contingent", "corroborate", "credence", "cursory", "debilitate",
        "deleterious", "demarcation", "denigrate", "derivative", "despot", "dichotomy",
        "diffident", "diligence", "discrepancy", "disparate", "disseminate", "dissident",
        "dogmatic", "ebullient", "eclectic", "efficacy", "elucidate", "emancipate",
        "empiricism", "enigmatic", "ephemeral", "epistemology", "equivocal", "erudite",
        "esoteric", "ethical", "euphemism", "exacerbate", "exigency", "expedient",
        "explicate", "expository", "extraneous", "fallacy", "fastidious", "fecund",
        "felicitous", "fidelity", "florid", "foment", "fortuitous", "garrulous",
        "germane", "gregarious", "hegemony", "heuristic", "hierarchy", "iconoclast",
        "idiosyncrasy", "immutable", "impartial", "imperative", "impermeable",
        "impetus", "implicit", "impute", "inadvertent", "incisive", "incontrovertible",
        "incumbent", "indefatigable", "indolent", "ineffable", "inexorable",
        "ingenuous", "inimical", "innocuous", "insidious", "insinuate", "intractable",
        "intransigent", "intrepid", "inundate", "inure", "inveterate", "irascible",
        "laconic", "lament", "laudable", "lenient", "lethargic", "levity", "limpid",
        "magnanimous", "maverick", "meticulous", "mollify", "mordant", "multifaceted",
        "myriad", "nebulous", "nonchalant", "norms", "obfuscate", "obsequious",
        "obstinate", "obviate", "officious", "onerous", "ostensible", "palliate",
        "paradigm", "parsimonious", "paucity", "pedantic", "penchant", "penurious",
        "perfunctory", "pernicious", "perpetuate", "perspicacious", "pertinent",
        "pious", "pivotal", "placate", "platitude", "plethora", "polemic", "pragmatic",
        "precarious", "precipitous", "predecessor", "predilection", "presage",
        "presumptuous", "pristine", "proclivity", "profligate", "prolific",
        "propensity", "propitiate", "prosaic", "protean", "pugnacious", "pulchritude",
        "quagmire", "quandary", "querulous", "quixotic", "quotidian", "raconteur",
        "rancor", "rapacious", "recalcitrant", "recondite", "redolent", "refulgent",
        "repudiate", "rescind", "resilient", "resplendent", "restive", "reticent",
        "reverent", "rhetoric", "sagacious", "salient", "sanctimonious", "sanguine",
        "sardonic", "scintilla", "scrupulous", "secular", "sedulous", "seminal",
        "serendipity", "solicitous", "solvent", "spurious", "staid", "stigma",
        "stipulate", "strident", "subjugate", "sublime", "subterranean", "succinct",
        "supercilious", "superfluous", "supplant", "surmise", "sycophant", "taciturn",
        "tantamount", "temerity", "tenable", "tenuous", "timorous", "torpid",
        "tractable", "trenchant", "ubiquitous", "unctuous", "undulate", "unequivocal",
        "untenable", "vacillate", "vapid", "veracity", "verbose", "vicissitude",
        "vindicate", "virulent", "viscous", "volatile", "voracious", "whimsical"
    )

    /** レベル分類: 単語・意味からLevel 1〜4を返す */
    fun classifyLevel(word: String, meaningEn: String): Int {
        val w = word.lowercase()
        val text = "$w ${meaningEn.lowercase()}"

        // 基礎語（Level 1）
        if (w in level1Words) return 1

        // 発展語（Level 4）: 専門性の高い語を最優先
        if (level4Roots.any { text.contains(it, ignoreCase = true) }) return 4

        // 応用語（Level 3）
        if (level3Roots.any { text.contains(it, ignoreCase = true) }) return 3

        // 標準語（Level 2）
        if (level2Roots.any { text.contains(it, ignoreCase = true) }) return 2

        // フォールバック: 語の長さで判断（短い語=基本、長い語=発展）
        return when {
            w.length <= 4 -> 1
            w.length <= 7 -> 2
            w.length <= 10 -> 3
            else -> 4
        }
    }

    /** TOEFLの3段階表示名（日本語）。内部level 1/2はBasicへ統合。 */
    fun levelLabelJa(level: Int): String = when (level) {
        1, 2 -> "TOEFL Basic"
        3 -> "TOEFL Standard"
        4, 5 -> "TOEFL Advanced"
        else -> "L$level"
    }

    /** TOEFLの3段階表示名（英語）。内部level 1/2はBasicへ統合。 */
    fun levelLabelEn(level: Int): String = when (level) {
        1, 2 -> "TOEFL Basic"
        3 -> "TOEFL Standard"
        4, 5 -> "TOEFL Advanced"
        else -> "L$level"
    }
}
