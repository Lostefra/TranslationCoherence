<%@page session="true"%><%@taglib uri="http://www.springframework.org/tags" prefix="sp"%><%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%><html version="XHTML+RDFa 1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/1999/xhtml http://www.w3.org/MarkUp/SCHEMA/xhtml-rdfa-2.xsd" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:xsd="http://www.w3.org/2001/XMLSchema#" xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:foaf="http://xmlns.com/foaf/0.1/">
<head data-color="${colorPair}" profile="http://www.w3.org/1999/xhtml/vocab">
<title>${results.getTitle()}&mdash;LodView</title>
<jsp:include page="inc/header.jsp"></jsp:include>
</head>
<body id="top">
	<article>
		<div id="logoBanner">
			<div id="logo">
				<!-- placeholder for logo -->
			</div>
		</div>
		<header>
			<hgroup>
				<h1>
					<span>Translation Coherence</span>
				</h1>
				<h2>
					<span>An ontology to describe language constructs in order to compare machine-generated ontologies.</span>
				</h2>
			</hgroup>
			<div id="abstract">
				<div class="value">This project aims at exploiting Knowledge Engineering technologies to compare translations across multiple languages by formal reasoning on them. Our goal is to understand which subtle modifications occur when going back and forth from a language to another using off-the-shelf translators (such as <a href="https://www.deepl.com/translator">DeepL</a>).
				<br>
				We have chosen the open-source <a href="https://www.statmt.org/europarl/">Europarl</a>  parallel corpus for this task. In particular we have taken the first 6 sentences from the English dataset and we have subsequently translated them to German, Italian and Chinese, and then we have translated them back to English. The choice of the languages is not incidental: we aimed at observing whether more differences pop up by translating towards more and more exotic languages with respect to English, thus we picked up a West Germanic language - German - a Latin language - Italian - and a non-European language - Chinese.
				<br>
				Once we have translated the sentences as described above, we employed the machine reader <a href="http://wit.istc.cnr.it/stlab-tools/fred/">FRED</a> to encode them as knowledge graphs. Starting with 6 sentences translated from 4 languages we ended up with 24 different ontologies.
				<br>
				The attempts we made to address the problem of computing the semantic differences between a pair of ontologies are described in the following sections.
				<br>
				All the code is available on <a href="https://github.com/Lostefra/TranslationCoherence">GitHub</a>.</div>
			</div>

		</header>

		<aside class="empty"></aside>

		<div id="directs">

			<div class="value">Here are the ontologies that can be browsed:
				<a href="http://localhost:8080/lodview/translation_coherence.owl">translation_coherence.owl</a> - the vocabulary for making statements to compare two given ontologies.
				<br>
				<b>sources</b>: the example source ontologies to be compared
				<i>original (english)</i>
				<ul>
					<li><a href="http://localhost:8080/lodview/en__sentence1.owl">en__sentence1.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence2.owl">en__sentence2.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence3.owl">en__sentence3.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence4.owl">en__sentence4.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence5.owl">en__sentence5.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en__sentence6.owl">en__sentence6.owl</a></li>
				</ul>
				<i>translated (english->italian->english)</i>
				<ul>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence1.owl">en_it_en__sentence1.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence2.owl">en_it_en__sentence2.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence3.owl">en_it_en__sentence3.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence4.owl">en_it_en__sentence4.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence5.owl">en_it_en__sentence5.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_it_en__sentence6.owl">en_it_en__sentence6.owl</a></li>
				</ul>
				<br>
				<b>outputs</b>: the example results of the comparison between pairs of ontologies
				<ul>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence1.owl">en_VS_en_it_en__sentence1.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence2.owl">en_VS_en_it_en__sentence2.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence3.owl">en_VS_en_it_en__sentence3.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence4.owl">en_VS_en_it_en__sentence4.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence5.owl">en_VS_en_it_en__sentence5.owl</a></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence6.owl">en_VS_en_it_en__sentence6.owl</a></li>
				</ul>

				To access resources defined within a certain ontology, simply type http://localhost:8080/lodview/<span style="text-color: red">namespace-name</span><span style="text-color: green">/resource-name</span> where <i>namespace-name</i> is the ontology (see above the available ones) and <i>resource-name</i> is the IRI of the resource, stripped of its prefix.

				Some examples:
				<ul>
					<li><a href="http://localhost:8080/lodview/translation_coherence.owl/Expression">Expression</a> (defined within <i>translation_coherence.owl)</i></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_cn_en__sentence2.owl/expression_1">expression_1</a> (defined within <i>en_VS_en_cn_en__sentence2.owl)</i></li>
					<li><a href="http://localhost:8080/lodview/translation_coherence.owl/Hierarchy">Hierarchy</a> (defined within <i>translation_coherence.owl)</i></li>
					<li><a href="http://localhost:8080/lodview/en_VS_en_it_en__sentence2.owl/hierarchy_1">hierarchy_1</a> (defined within <i>en_VS_en_it_en__sentence2.owl)</i></li>
				</ul>
			</div>

		</div>

		<div id="inverses" class="empty"></div> 
		<jsp:include page="inc/custom_footer.jsp"></jsp:include>
	</article>
	<jsp:include page="inc/footer.jsp"></jsp:include>

</body>
</html>
